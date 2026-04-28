import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow info/warning logs

import cv2
import numpy as np
import random
import time
import pandas as pd
import datetime
import threading
import platform
from flask import Flask, render_template, Response, jsonify, send_from_directory
from database import DatabaseManager

# Try to import RetinaFace; fall back to Haar Cascade if unavailable
try:
    from retinaface import RetinaFace
    RETINA_FACE_AVAILABLE = True
except Exception:
    RETINA_FACE_AVAILABLE = False

# Track if RetinaFace model loads successfully at runtime (prevents repeated errors)
_retinaface_working = RETINA_FACE_AVAILABLE

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask with correct template and static folders
app = Flask(__name__, 
            template_folder=current_dir,
            static_folder=os.path.join(current_dir, 'static'))

# Initialize database
db = DatabaseManager()

# Update device status on startup
db.update_device_status('Camera', 'Active', 'Main entrance camera - ready')
db.update_device_status('Face Recognition AI', 'Active', 'TensorFlow model - ready')
db.update_device_status('Database', 'Active', 'PostgreSQL - ready')
db.update_device_status('Flask Server', 'Active', 'Port 5000 - running')

# Sample student names for demo (in real scenario, you'd use face recognition)
STUDENT_NAMES = ['Abhiraj Srivastava', 'Rahul Sharma', 'Sanya Malhotra', 'Vikram Singh', 'Anjali Rao', 'Arya Panday']


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
            
        # Use DirectShow backend on Windows for better compatibility
        if platform.system() == 'Windows':
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            self.camera = cv2.VideoCapture(0)
            
        # Allow camera warm-up time
        time.sleep(1)
        
        if not self.camera or not self.camera.isOpened():
            print("Warning: Camera could not be opened. Video feed will not work.")
            self.camera = None
            return False
            
        self.stopped = False
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        return True
        
    def _cleanup_detected_faces(self):
        """Remove old face tracking entries to prevent memory growth."""
        now = datetime.datetime.now()
        old = [k for k, v in self.detected_faces.items() if (now - v).seconds > 60]
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
                
            # Process frame (face detection overlay)
            try:
                frame = self._process_frame(frame)
            except Exception as e:
                # Log once only to prevent console spam
                print(f"Face detection error: {e}")
                break
                
            # Encode frame
            encoded = _encode_frame(frame)
            
            with self.lock:
                self.frame = encoded
                
            self._frame_count += 1
            if self._frame_count % 100 == 0:
                self._cleanup_detected_faces()
                
            time.sleep(0.03)  # ~30 FPS cap
            
    def _process_frame(self, frame):
        """Apply face detection overlay and log attendance."""
        global _retinaface_working
        used_retina = False
        
        if _retinaface_working:
            try:
                faces = RetinaFace.detect_faces(frame)
                if isinstance(faces, dict):
                    for key in faces:
                        identity = faces[key]
                        facial_area = identity["facial_area"]
                        x1, y1, x2, y2 = facial_area
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(frame, 'Face Detected', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        student = random.choice(STUDENT_NAMES)
                        face_id = f"{x1}_{y1}"
                        if face_id not in self.detected_faces or (datetime.datetime.now() - self.detected_faces[face_id]).seconds > 2:
                            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            db.add_attendance(student, current_time, 'Present', 'RetinaFace detected')
                            self.detected_faces[face_id] = datetime.datetime.now()
                    used_retina = True
            except Exception as e:
                # Disable RetinaFace permanently after first failure to prevent error spam
                _retinaface_working = False
                print(f"RetinaFace failed (switching to Haar Cascade): {e}")
                
        if not used_retina:
            # Fall back to Haar Cascade (no external model downloads needed)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, 'Face Detected', (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                student = random.choice(STUDENT_NAMES)
                face_id = f"{x}_{y}"
                if face_id not in self.detected_faces or (datetime.datetime.now() - self.detected_faces[face_id]).seconds > 2:
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    db.add_attendance(student, current_time, 'Present', 'Face detected')
                    self.detected_faces[face_id] = datetime.datetime.now()
                    
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


def generate_frames():
    """MJPEG generator that never hangs — always yields a frame."""
    # Start camera thread on first request
    camera_available = camera_thread.start()
    
    if not camera_available:
        frame = _placeholder_frame('Camera Not Available')
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.5)
        return
    
    # Wait briefly for the first captured frame
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
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/script.js')
def serve_script():
    return send_from_directory(current_dir, 'script.js')

@app.route('/api/data')
def get_data():
    """Returns attendance data as JSON"""
    logs = db.get_all_attendance_logs(limit=100)
    return jsonify(logs)

@app.route('/api/stats')
def get_stats():
    """Returns summary stats for dashboard cards"""
    stats = db.get_attendance_stats()
    return jsonify(stats)

@app.route('/api/students')
def get_students():
    """Returns all students"""
    students = db.get_all_students()
    return jsonify(students)

@app.route('/api/attendance-logs')
def get_attendance_logs():
    """Returns attendance logs"""
    logs = db.get_all_attendance_logs()
    return jsonify(logs)

@app.route('/api/attendance-logs/<date>')
def get_attendance_by_date(date):
    """Returns attendance logs for a specific date"""
    logs = db.get_attendance_by_date(date)
    return jsonify(logs)

@app.route('/api/weekly-stats')
def get_weekly_stats():
    """Returns weekly statistics"""
    stats = db.get_weekly_stats()
    return jsonify(stats)

@app.route('/api/device-status')
def get_device_status():
    """Returns device status"""
    devices = db.get_device_status()
    return jsonify(devices)

if __name__ == '__main__':
    # use_reloader=False prevents the camera from being locked by the reloader process
    app.run(debug=True, use_reloader=False, threaded=True)
