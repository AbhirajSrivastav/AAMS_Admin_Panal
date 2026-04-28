"""
app/services/face_recognition_service.py
========================================
Face Recognition Service for the Attendance Management System.

This module handles everything related to face detection and identification:
    - Loading student images from disk
    - Computing 128-dimensional face encodings
    - Averaging multiple encodings per student for robustness
    - Matching detected faces against the known database

How image_data is used during face recognition:
------------------------------------------------
1. At startup (or when `/api/reload-faces` is called), the service scans
   the folder configured as IMAGE_DATA_DIR (default: app/image_data/).

2. Inside that folder, each sub-folder represents one student.
   Example structure:
       app/image_data/
           student_001/
               img1.jpg
               img2.jpg
               img3.jpg
           student_002/
               photo1.png
               photo2.jpg

   The folder name becomes the student's display name for recognition.

3. Every image file ending in .jpg, .jpeg, .png, .bmp, or .webp is loaded
   using the face_recognition library.

4. For each image, the library detects face locations and extracts a
   128-d encoding vector. If a face is not found in an image, a warning
   is printed and that image is skipped.

5. If a student has multiple valid images, ALL their encodings are averaged
   element-wise. This produces a single "representative" encoding that is
   more robust to lighting, pose, and expression variations than any
   single photo.

6. These averaged encodings are stored in memory (RAM) as:
       known_face_encodings : list of numpy arrays
       known_face_names     : list of student names (parallel index)

How matching works (encoding + comparison):
--------------------------------------------
When a video frame arrives from the camera:

  A. The OpenCV BGR frame is converted to RGB because face_recognition
     expects RGB images.

  B. `face_recognition.face_locations(rgb_frame)` finds all faces in the
     frame using a Histogram of Oriented Gradients (HOG) model or CNN
     (depending on library build).

  C. `face_recognition.face_encodings(rgb_frame, face_locations)` extracts
     the 128-d encoding for each detected face.

  D. `face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance)`
     returns a boolean list. A value is True if the Euclidean distance between
     the unknown encoding and a known encoding is LESS than the tolerance
     (default 0.55). Lower tolerance = stricter matching.

  E. If any True values exist, `face_recognition.face_distance()` computes
     the exact numeric distances, and the student with the SMALLEST distance
     (best match) is selected.

  F. The matched name is drawn as an overlay on the video frame, and the
     attendance service is triggered to log the check-in.

How new student images are added:
-----------------------------------
1. Create a new sub-folder under IMAGE_DATA_DIR using the student's
   unique identifier or sanitized name:
       mkdir app/image_data/student_007

2. Copy 3-5 clear face photos into that folder. Variety helps accuracy:
   - Different lighting (bright, dim)
   - Different angles (front, slight left/right)
   - Different expressions (neutral, slight smile)

3. Either restart the Flask server OR send a POST request to:
       POST /api/reload-faces
   This re-scans the disk without restarting the whole app.

Dependencies:
    - face_recognition (Python wrapper around dlib)
    - numpy (for encoding averaging)
    - opencv-python (for frame conversion)
"""

import os
import numpy as np
from typing import List, Tuple

# Optional import: face_recognition may not be installed on all environments
FACE_RECOGNITION_AVAILABLE = False
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except Exception as e:
    print(f'[WARN] face_recognition not available: {e}')


class FaceRecognitionService:
    """
    Service class that encapsulates all face recognition operations.

    Attributes:
        image_dir (str): Root folder containing student sub-folders.
        tolerance (float): Distance threshold for a match (default 0.55).
        known_face_encodings (List[np.ndarray]): Averaged encodings per student.
        known_face_names (List[str]): Parallel list of student names.
    """

    def __init__(self, image_dir: str = None, tolerance: float = 0.55):
        """
        Initialize the service.

        Args:
            image_dir (str): Path to the image_data root. If None, uses
                             the IMAGE_DATA_DIR env var or defaults to
                             'app/image_data' relative to project root.
            tolerance (float): Matching strictness (lower = stricter).
        """
        if image_dir is None:
            # Resolve default path relative to this file's location
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            image_dir = os.getenv('IMAGE_DATA_DIR', os.path.join(base, 'app', 'image_data'))

        self.image_dir = image_dir
        self.tolerance = tolerance
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_names: List[str] = []

    # ------------------------------------------------------------------
    # Loading & encoding
    # ------------------------------------------------------------------

    def load_known_faces(self) -> None:
        """
        Scan image_dir and populate known_face_encodings / known_face_names.

        This should be called once at startup and again whenever new
        student images are added to disk.
        """
        self.known_face_encodings = []
        self.known_face_names = []

        if not FACE_RECOGNITION_AVAILABLE:
            print('[INFO] face_recognition not installed; skipping known-face loading.')
            return

        if not os.path.isdir(self.image_dir):
            print(f'[WARN] Image data directory not found: {self.image_dir}')
            return

        # Iterate over each sub-folder (one per student)
        for student_name in sorted(os.listdir(self.image_dir)):
            student_path = os.path.join(self.image_dir, student_name)
            if not os.path.isdir(student_path):
                continue  # skip stray files in the root

            encodings = self._load_student_encodings(student_path, student_name)
            if encodings:
                # Average all valid encodings for this student
                avg_encoding = np.mean(encodings, axis=0)
                self.known_face_encodings.append(avg_encoding)
                self.known_face_names.append(student_name)
                print(f'[OK] Registered {len(encodings)} encoding(s) for "{student_name}"')
            else:
                print(f'[WARN] No valid face encodings for "{student_name}"')

        print(f'[INFO] Loaded {len(self.known_face_names)} student(s) for face recognition.')

    def _load_student_encodings(self, student_path: str, student_name: str) -> List[np.ndarray]:
        """
        Load all valid face encodings from a single student's image folder.

        Args:
            student_path (str): Absolute path to the student's image folder.
            student_name (str): Human-readable name (for logging only).

        Returns:
            List[np.ndarray]: List of 128-d face encodings found in the folder.
        """
        encodings = []
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

        for fname in os.listdir(student_path):
            if not fname.lower().endswith(valid_extensions):
                continue

            img_path = os.path.join(student_path, fname)
            try:
                # face_recognition uses RGB (PIL-style) images
                img = face_recognition.load_image_file(img_path)
                face_encs = face_recognition.face_encodings(img)

                if face_encs:
                    # Take the first face found in the image
                    encodings.append(face_encs[0])
                    print(f'[OK] Loaded face for "{student_name}" from {fname}')
                else:
                    print(f'[WARN] No face found in {img_path}')
            except Exception as e:
                print(f'[ERROR] Failed to process {img_path}: {e}')

        return encodings

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    def identify_faces(self, rgb_frame) -> List[Tuple[Tuple[int, int, int, int], str]]:
        """
        Detect and identify all faces in a single RGB video frame.

        Args:
            rgb_frame (np.ndarray): Image in RGB format (H x W x 3).

        Returns:
            List of tuples: ((top, right, bottom, left), name)
                - name is "Unknown" if no match is found within tolerance.
        """
        if not FACE_RECOGNITION_AVAILABLE or not self.known_face_encodings:
            return []

        # 1. Find face bounding boxes
        face_locations = face_recognition.face_locations(rgb_frame)
        # 2. Extract 128-d encodings for each detected face
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        results = []
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = self._match_face(face_encoding)
            results.append(((top, right, bottom, left), name))

        return results

    def _match_face(self, face_encoding: np.ndarray) -> str:
        """
        Compare one unknown face encoding against the known database.

        Steps:
            1. compare_faces() -> boolean list (distance < tolerance)
            2. If any True, compute exact distances with face_distance()
            3. Pick the index with the minimum distance (best match)
            4. Verify the boolean match for that index is still True

        Args:
            face_encoding (np.ndarray): 128-d vector from camera frame.\n
        Returns:
            str: Matched student name, or "Unknown" if no good match.
        """
        matches = face_recognition.compare_faces(
            self.known_face_encodings, face_encoding, tolerance=self.tolerance
        )
        name = 'Unknown'

        if True in matches:
            # Compute numeric distances for all known faces
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, face_encoding
            )
            best_match_index = int(np.argmin(face_distances))

            # Double-check the best match actually passed the tolerance
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

        return name

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def reload(self) -> dict:
        """
        Re-scan disk and reload all face encodings.

        Returns:
            dict: Summary with student count and list of loaded names.
        """
        self.load_known_faces()
        return {
            'status': 'ok',
            'students_loaded': len(self.known_face_names),
            'students': self.known_face_names
        }

