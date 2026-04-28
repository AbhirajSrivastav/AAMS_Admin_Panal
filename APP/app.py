import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow info/warning logs

import cv2
import numpy as np
import time
import datetime
import threading
import platform
from flask import Flask, render_template, Response, jsonify, send_from_directory
from database import DatabaseManager

# ---------------------------------------------------------------------------
# Face Recognition Setup
# ---------------------------------------------------------------------------
FACE_RECOGNITION_AVAILABLE = False
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except Exception as e:
    print(f"[WARN] face_recognition not available: {e}")

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
IMAGE_DATA_DIR = os.path.join(current_dir, 'Image_DATA')

# Known faces: list of (name, encoding)
known_face_encodings = []
known_face_names = []


def load_known_faces(image_dir=IMAGE_DATA_DIR):
    """Load student face images from Image_DATA/<name>/ folders."""
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []

    if not FACE_RECOGNITION_AVAILABLE:
        print("[INFO] face_recognition not installed; skipping known-face loading.")
        return

    if not os.path.isdir(image_dir):
        print(f"[WARN] Image data directory not found: {image_dir}")
        return

    for student_name in sorted(os.listdir(image_dir)):
        student_path = os.path.join(image_dir, student_name)
        if not os.path.isdir(student_path):
            continue

        encodings = []
        for fname in os.listdir(student_path):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                img_path = os.path.join(student_path, fname)
                try:
                    img = face_recognition.load_image_file(img_path)
                    # Get first face encoding from the image
                    face_encs = face_recognition.face_encodings(img)
                    if face_encs:
                        encodings.append(face_encs[0])
                        print(f"[OK] Loaded face for '{student_name}' from {fname}")
                    else:
                        print(f"[WARN] No face found in {img_path}")
                except Exception as e:
                    print(f"[ERROR] Failed to process {img_path}: {e}")

        if encodings:
            # Average all encodings for this student for better accuracy
            avg_encoding = np.mean(encodings, axis=0)
            known_face_encodings.append(avg_encoding)
            known_face_names.append(student_name)
        else:
            print(f"[WARN] No valid face encodings for '{student_name}'")

    print(f"[INFO] Loaded {len(known_face_names)} student(s) for face recognition.")


def ensure_student_in_db(name):
    """Ensure a student exists in the database; auto-create if missing."""
    students = db.get_all_students()
    for s in students:
        if s.get('name') == name:
            return s['id']

    # Auto-create student with a generated ID
    import re
    safe_id = re.sub(r'[^a-zA-Z0-9]', '', name).upper()[:6] or 'STU001'
    # Make unique if needed
    existing_ids = {s['student_id'] for s in students}
    original_safe = safe_id
    counter = 1
    while safe_id in existing_ids:
        safe_id = f"{original_safe[:3]}{counter:03d}"
        counter += 1

    email = f"{name.lower().replace(' ', '.')}@school.com"
    db.add_student(name, safe_id, email)
    print(f"[INFO] Auto-registered new student: {name} ({safe_id})")

    # Return new student ID
    students = db.get_all_students()
    for s in students:
        if s.get('name') == name:
            return s['id']
    return None


# ---------------------------------------------------------------------------
# Flask App Setup
# ---------------------------------------------------------------------------
app = Flask(__name__,
            template_folder=current_dir,
            static_folder=os.path.join(current_dir, 'static'))

# Initialize database
db = DatabaseManager()

# Load known faces from Image_DATA
load_known_faces()

# Update device status on startup
db.update_device_status('Camera', 'Active', 'Main entrance camera - ready')
db.update_device_status('Face Recognition AI', 'Active',
                        f"face_recognition loaded: {len(known_face_names)} student(s)")
db.update_device_status('Database', 'Active', 'PostgreSQL - ready')
db.update_device_status('Flask Server', 'Active', 'Port 5000 - running')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _encode_frame(frame):
    """Encode an OpenCV frame to JPEG bytes for MJPEG streaming."""
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        return None
    return buffer.tobytes()


def _placeholder_frame(text, width=640, height=480):
    """Generate a placeholder image with the given text."""
    blank = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(blank, text, (120, height // 2),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return _encode_frame(blank)


# ---------------------------------------------------------------------------
# Camera Thread with Real Face Recognition
# ---------------------------------------------------------------------------
class CameraThread:
    def __init__(self):
        self.camera = None
        self.frame = None
        self.stopped = False
        self.thread = None
        self.lock = threading.Lock()
        self.detected_faces = {}
        self._frame_count = 0

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
            print("[WARN] Camera could not be opened. Video feed will not work.")
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
                print(f"[ERROR] Face detection error: {e}")

            encoded = _encode_frame(frame)
            with self.lock:
                self.frame = encoded

            self._frame_count += 1
            if self._frame_count % 100 == 0:
                self._cleanup_detected_faces()

            time.sleep(0.03)

    def _process_frame(self, frame):
        """Apply face detection / recognition overlay and log attendance."""
        if FACE_RECOGNITION_AVAILABLE and known_face_encodings:
            return self._process_with_face_recognition(frame)
        else:
            return self._process_with_haar(frame)

    def _process_with_face_recognition(self, frame):
        """Use face_recognition library to identify students."""
        # Convert BGR (OpenCV) to RGB (face_recognition)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare against known faces
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding, tolerance=0.55)
            name = "Unknown"

            if True in matches:
                # Pick the best match (smallest face distance)
                face_distances = face_recognition.face_distance(
                    known_face_encodings, face_encoding)
                best_match_index = int(np.argmin(face_distances))
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            # Draw rectangle and label
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Log attendance for known students (throttle: once per 2 sec)
            if name != "Unknown":
                face_id = f"{left}_{top}_{name}"
                now = datetime.datetime.now()
                if face_id not in self.detected_faces or \
                   (now - self.detected_faces[face_id]).seconds > 2:
                    current_time = now.strftime('%Y-%m-%d %H:%M:%S')
                    db.add_attendance(name, current_time, 'Present',
                                      'Face recognized via camera')
                    self.detected_faces[face_id] = now

        return frame

    def _process_with_haar(self, frame):
        """Fallback: Haar Cascade face detection (no identification)."""
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


camera_thread = CameraThread()


# ---------------------------------------------------------------------------
# MJPEG Stream Generator
# ---------------------------------------------------------------------------
def generate_frames():
    """MJPEG generator that never hangs — always yields a frame."""
    camera_available = camera_thread.start()

    if not camera_available:
        frame = _placeholder_frame('Camera Not Available')
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.5)
        return

    frame = _placeholder_frame('Camera Initializing...')
    for _ in range(100):
        latest = camera_thread.get_frame()
        if latest is not None:
            frame = latest
            break
        time.sleep(0.05)

    while True:
        latest = camera_thread.get_frame()
        if latest is not None:
            frame = latest

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.03)


# ---------------------------------------------------------------------------
# Flask Routes
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('Index.html')


@app.route('/student-directory')
def student_directory():
    return render_template('StudentDirectory.html')


@app.route('/attendance-logs')
def attendance_logs():
    return render_template('AttendanceLogs.html')


@app.route('/reports')
def reports():
    return render_template('Reports.html')


@app.route('/device-status')
def device_status():
    return render_template('DeviceStatus.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/script.js')
def serve_script():
    return send_from_directory(current_dir, 'script.js')


@app.route('/api/data')
def get_data():
    """Returns attendance data as JSON."""
    logs = db.get_all_attendance_logs(limit=100)
    return jsonify(logs)


@app.route('/api/stats')
def get_stats():
    """Returns summary stats for dashboard cards."""
    stats = db.get_attendance_stats()
    return jsonify(stats)


@app.route('/api/students')
def get_students():
    """Returns all students."""
    students = db.get_all_students()
    return jsonify(students)


@app.route('/api/attendance-logs')
def get_attendance_logs():
    """Returns attendance logs."""
    logs = db.get_all_attendance_logs()
    return jsonify(logs)


@app.route('/api/attendance-logs/<date>')
def get_attendance_by_date(date):
    """Returns attendance logs for a specific date."""
    logs = db.get_attendance_by_date(date)
    return jsonify(logs)


@app.route('/api/weekly-stats')
def get_weekly_stats():
    """Returns weekly statistics."""
    stats = db.get_weekly_stats()
    return jsonify(stats)


@app.route('/api/device-status')
def get_device_status():
    """Returns device status."""
    devices = db.get_device_status()
    return jsonify(devices)


@app.route('/api/reload-faces', methods=['POST'])
def reload_faces():
    """Admin endpoint to reload face images from Image_DATA."""
    load_known_faces()
    return jsonify({
        'status': 'ok',
        'students_loaded': len(known_face_names),
        'students': known_face_names
    })


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, threaded=True)

