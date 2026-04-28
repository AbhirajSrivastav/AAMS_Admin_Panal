"""
app/utils/camera.py
===================
Camera thread and video stream utilities.

This module handles the low-level video capture and frame processing.
It is isolated from route files so that it can be unit-tested or
replaced with a mock camera in CI environments.

Usage:
    from app.utils.camera import CameraManager
    camera = CameraManager()
    camera.start()
    frame_bytes = camera.get_frame()
"""

import cv2
import time
import threading
import platform
import datetime
import numpy as np
from app.services.face_recognition_service import FaceRecognitionService
from app.services.attendance_service import AttendanceService


class CameraManager:
    """
    Manages the webcam capture thread and face recognition overlay.

    Attributes:
        camera: cv2.VideoCapture instance.
        frame (bytes): Latest JPEG-encoded frame.
        stopped (bool): Flag to stop the thread.
        detected_faces (dict): Throttle cache for face attendance logging.
    """

    def __init__(self):
        self.camera = None
        self.frame = None
        self.stopped = False
        self.thread = None
        self.lock = threading.Lock()
        self.detected_faces = {}
        self._frame_count = 0
        self.face_service = FaceRecognitionService()
        self.attendance_service = AttendanceService()

    def start(self):
        """Initialize and start the camera capture thread."""
        if self.thread is not None:
            return True

        if platform.system() == 'Windows':
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            self.camera = cv2.VideoCapture(0)

        time.sleep(1)

        if not self.camera or not self.camera.isOpened():
            print('[WARN] Camera could not be opened. Video feed will not work.')
            self.camera = None
            return False

        self.stopped = False
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        return True

    def _cleanup_detected_faces(self):
        """Remove old face tracking entries to prevent memory growth."""
        now = datetime.datetime.now()
        old = [k for k, v in self.detected_faces.items()
               if (now - v).seconds > 60]
        for k in old:
            del self.detected_faces[k]

    def _update(self):
        """Background loop: continuously read and process frames."""
        while not self.stopped:
            if self.camera is None:
                time.sleep(0.1)
                continue

            success, frame = self.camera.read()
            if not success:
                time.sleep(0.01)
                continue

            try:
                frame = self._process_frame(frame)
            except Exception as e:
                print(f'[ERROR] Face detection error: {e}')

            from app.utils.helpers import encode_frame_to_jpeg
            encoded = encode_frame_to_jpeg(frame)
            with self.lock:
                self.frame = encoded

            self._frame_count += 1
            if self._frame_count % 100 == 0:
                self._cleanup_detected_faces()

            time.sleep(0.03)

    def _process_frame(self, frame):
        """Apply face detection / recognition overlay and log attendance."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_service.identify_faces(rgb_frame)

        for (top, right, bottom, left), name in results:
            color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if name != 'Unknown':
                face_id = f'{left}_{top}_{name}'
                now = datetime.datetime.now()
                if face_id not in self.detected_faces or \
                   (now - self.detected_faces[face_id]).seconds > 2:
                    self.attendance_service.mark_attendance(name)
                    self.detected_faces[face_id] = now

        # Also run Haar fallback to show any face boxes
        if not results:
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, 'Face Detected', (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame

    def get_frame(self):
        """Get the latest encoded frame (thread-safe)."""
        with self.lock:
            return self.frame

    def stop(self):
        """Stop the camera thread and release resources."""
        self.stopped = True
        if self.thread:
            self.thread.join(timeout=1)
        if self.camera:
            self.camera.release()

