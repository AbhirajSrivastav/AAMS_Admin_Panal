"""
app/utils/helpers.py
====================
General helper utilities used across the application.

These are small, stateless functions that don't fit into a specific
service but are reused in multiple places (routes, camera thread, etc.).
"""

import cv2
import numpy as np
import time
from typing import Optional


def encode_frame_to_jpeg(frame: np.ndarray) -> Optional[bytes]:
    """
    Encode an OpenCV BGR frame to JPEG bytes for MJPEG streaming.

    Args:
        frame (np.ndarray): OpenCV image array (H x W x 3).

    Returns:
        bytes or None: JPEG-encoded image bytes, or None on failure.
    """
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return None
    return buffer.tobytes()


def generate_placeholder_frame(text: str, width: int = 640, height: int = 480) -> bytes:
    """
    Create a placeholder black image with red text.
    Used when the camera is unavailable or initializing.

    Args:
        text (str): Message to display.
        width (int): Image width in pixels.
        height (int): Image height in pixels.

    Returns:
        bytes: JPEG-encoded placeholder image.
    """
    blank = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(
        blank, text, (120, height // 2),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
    )
    encoded = encode_frame_to_jpeg(blank)
    return encoded if encoded else b''


def generate_safe_student_id(name: str, existing_ids: set) -> str:
    """
    Generate a unique student_id from a full name.

    Algorithm:
        1. Strip non-alphanumeric characters and uppercase the name.
        2. Truncate to 6 characters.
        3. If that ID already exists, append an incrementing numeric suffix
           until a unique value is found.

    Args:
        name (str): Full student name.
        existing_ids (set): Currently used student_id strings.

    Returns:
        str: A unique 6-character uppercase ID.
    """
    import re
    safe_id = re.sub(r'[^a-zA-Z0-9]', '', name).upper()[:6] or 'STU001'
    original = safe_id
    counter = 1
    while safe_id in existing_ids:
        safe_id = f'{original[:3]}{counter:03d}'
        counter += 1
    return safe_id


def student_folder_name(student_id: str, name: str) -> str:
    """
    Convert a student ID and name into a safe filesystem folder name.

    This keeps image_data/ folders readable and consistent.
    Example: ('STU001', 'Abhiraj Srivastava') -> 'STU001_Abhiraj_Srivastava'

    Args:
        student_id (str): Unique student identifier.
        name (str): Full name.

    Returns:
        str: Sanitized folder name.
    """
    import re
    safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
    return f'{student_id}_{safe_name}'


def generate_frames(camera_manager):
    """
    MJPEG generator that yields encoded camera frames.

    Args:
        camera_manager: CameraManager instance providing get_frame().

    Yields:
        bytes: MJPEG frame boundary + JPEG data.
    """
    camera_available = camera_manager.start()

    if not camera_available:
        frame = generate_placeholder_frame('Camera Not Available')
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.5)
        return

    frame = generate_placeholder_frame('Camera Initializing...')
    for _ in range(100):
        latest = camera_manager.get_frame()
        if latest is not None:
            frame = latest
            break
        time.sleep(0.05)

    while True:
        latest = camera_manager.get_frame()
        if latest is not None:
            frame = latest

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03)

