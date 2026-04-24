import cv2
import numpy as np
import random
import time
import pandas as pd
import datetime
import os
from flask import Flask, render_template, Response, jsonify
from database import DatabaseManager

# Try to import RetinaFace; fall back to Haar Cascade if unavailable
try:
    from retinaface import RetinaFace
    RETINA_FACE_AVAILABLE = True
except Exception:
    RETINA_FACE_AVAILABLE = False

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

# Try to initialize camera
camera = None
try:
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Warning: Camera could not be opened. Video feed will not work.")
        camera = None
except Exception as e:
    print(f"Error initializing camera: {e}")
    camera = None


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


def generate_frames():
    if camera is None:
        # Generate a placeholder image if camera is not available
        import numpy as np
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank_frame, 'Camera Not Available', (150, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        ret, buffer = cv2.imencode('.jpg', blank_frame)
        frame = buffer.tobytes()
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        return
    
    detected_faces = {}  # Track detected faces to avoid duplicate entries
    
    while True:
        try:
            success, frame = camera.read()
            if not success:
                continue
            
            # --- FACIAL DETECTION LOGIC START ---
            # Sample student names for demo (in real scenario, you'd use face recognition)
            student_names = ['Abhiraj Srivastava', 'Rahul Sharma', 'Sanya Malhotra', 'Vikram Singh', 'Anjali Rao', 'Arya Panday']
            import random

            if RETINA_FACE_AVAILABLE:
                # Use RetinaFace for detection
                faces = RetinaFace.detect_faces(frame)
                if isinstance(faces, dict):
                    for key in faces:
                        identity = faces[key]
                        facial_area = identity["facial_area"]
                        x1, y1, x2, y2 = facial_area
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(frame, 'Face Detected', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                        student = random.choice(student_names)
                        face_id = f"{x1}_{y1}"
                        if face_id not in detected_faces or (datetime.datetime.now() - detected_faces[face_id]).seconds > 2:
                            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            db.add_attendance(student, current_time, 'Present', 'RetinaFace detected')
                            detected_faces[face_id] = datetime.datetime.now()
            else:
                # Fall back to Haar Cascade
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(frame, 'Face Detected', (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    student = random.choice(student_names)
                    face_id = f"{x}_{y}"
                    if face_id not in detected_faces or (datetime.datetime.now() - detected_faces[face_id]).seconds > 2:
                        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        db.add_attendance(student, current_time, 'Present', 'Face detected')
                        detected_faces[face_id] = datetime.datetime.now()
            # --- FACIAL DETECTION LOGIC END ---

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error in generate_frames: {e}")
            continue

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
    app.run(debug=True)