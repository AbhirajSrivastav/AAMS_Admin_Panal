🚀 AAMS — Automated Attendance Management System
Advanced AI-Powered Face Recognition Attendance Platform
Python Flask PostgreSQL OpenCV Status

⚡ Real-Time Face Recognition • Smart Attendance Tracking • Modular Flask Architecture
📌 Overview
AAMS (Automated Attendance Management System) is a production-ready AI-powered attendance platform built using Flask, PostgreSQL, OpenCV, and face_recognition.

The system automatically detects students through a live camera feed, identifies them using facial recognition, and stores attendance records in a PostgreSQL database with real-time analytics support.

✨ Core Features
🎥 Real-time face detection & recognition
🧠 AI-based attendance automation
🗄 PostgreSQL database integration
📊 Interactive analytics dashboard
🌐 RESTful API architecture
⚡ MJPEG live video streaming
🏗 Modular Flask application structure
📈 Attendance reports & statistics
🔄 Dynamic face dataset reloading
🛡 Production-ready scalable architecture
🏗 Project Structure
AAMS_Admin_Panal/
│
├── run.py                     # Application entry point
├── wsgi.py                    # Production WSGI server entry
├── app.py                     # Compatibility shim
├── requirements.txt
├── .env
├── API_DOCUMENTATION.md
├── README.md
│
├── APP/
│   ├── __init__.py            # Flask application factory
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── attendance_routes.py
│   │   ├── student_routes.py
│   │   └── dashboard_routes.py
│   │
│   ├── services/
│   │   ├── face_recognition_service.py
│   │   ├── attendance_service.py
│   │   └── report_service.py
│   │
│   ├── database/
│   │   └── db.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── reports.html
│   │   ├── device_status.html
│   │   ├── student_directory.html
│   │   └── attendance_logs.html
│   │
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── main.js
│   │       ├── charts.js
│   │       └── reports.js
│   │
│   ├── Image_DATA/
│   │   └── (student images)
│   │
│   └── utils/
│       ├── camera.py
│       └── helpers.py
🧠 Face Recognition Workflow
📁 Dataset Structure
APP/Image_DATA/
│
├── Abhiraj/
│   ├── img1.jpg
│   ├── img2.jpg
│   └── img3.jpg
│
├── Rahul/
│   ├── face1.jpg
│   ├── face2.jpg
│   └── face3.jpg
⚙️ Recognition Pipeline
1️⃣ Dataset Scanning
The system scans all student folders inside Image_DATA/.

2️⃣ Face Encoding
Each image is converted into a 128-dimensional face embedding vector using:

face_recognition.face_encodings()
3️⃣ Encoding Averaging
Multiple encodings for a student are averaged to improve:

Lighting robustness
Expression handling
Pose variation tolerance
4️⃣ Face Detection
Incoming frames are processed using:

face_recognition.face_locations()
5️⃣ Face Matching
Detected faces are matched against stored encodings using:

face_recognition.compare_faces()
6️⃣ Attendance Logging
Matched students are automatically recorded into PostgreSQL with timestamps.

⚙️ Installation
1️⃣ Clone Repository
git clone https://github.com/your-username/AAMS.git
cd AAMS
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Configure Environment Variables
Create a .env file:

SECRET_KEY=your-secret-key

DB_HOST=localhost
DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
4️⃣ Create PostgreSQL Database
CREATE DATABASE attendance_db;
🚀 Running the Application
Development Mode
python run.py
Production Mode
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 2
Open Application
http://localhost:5000
🌐 API Endpoints
Endpoint	Method	Description
/	GET	Dashboard Home
/student-directory	GET	Student Directory
/attendance-logs	GET	Attendance Logs
/reports	GET	Analytics Dashboard
/device-status	GET	System Health
/video_feed	GET	Live Camera Stream
/api/stats	GET	Today's Statistics
/api/data	GET	Recent Attendance Data
/api/students	GET	Student Records
/api/attendance-logs	GET	Attendance Logs API
/api/attendance-logs/<date>	GET	Logs By Date
/api/weekly-stats	GET	Weekly Reports
/api/device-status	GET	Device Monitoring
/api/reload-faces	POST	Reload Face Dataset
🏛 Application Factory Architecture
AAMS uses Flask's Application Factory Pattern.

Benefits
Modular blueprint architecture
Better scalability
Easier testing
Environment-based configurations
SaaS-ready foundation
Cleaner service separation
📈 SaaS Scalability Roadmap
Feature	Status
Modular Blueprints	✅ Ready
Service Layer	✅ Ready
Config Environments	✅ Ready
JWT Authentication	🚧 Planned
SQLAlchemy ORM	🚧 Planned
Alembic Migrations	🚧 Planned
Celery Task Queue	🚧 Planned
Multi-Tenant Support	🚧 Planned
Email Notifications	🚧 Planned
🧪 Troubleshooting
🎥 Camera Not Working
Try changing camera index:

cv2.VideoCapture(0)
to:

cv2.VideoCapture(1)
🗄 Database Connection Failed
Verify PostgreSQL service:

pg_isready -h localhost -p 5432
⚠ face_recognition Installation Issue
pip install face-recognition
Note: face_recognition requires dlib and CMake.

📜 License
This project is provided for:

Educational Use
Institutional Deployment
Research & Learning
⭐ AAMS — Automated Attendance Management System
Built with Flask • PostgreSQL • OpenCV • AI
