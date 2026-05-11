# AAMS - AI Attendance Management System

**Advanced Face Recognition Based Attendance Management System with PostgreSQL Database Integration**

![Python](https://img.shields.io/badge/Python-3.7+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-red)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## Overview

AAMS is a production-ready, modular Flask application that combines:
- **Real-time video processing** with face detection & recognition
- **Automatic attendance logging** to PostgreSQL database
- **Interactive dashboard** with live analytics
- **Multi-page web interface** for student & attendance management
- **RESTful API** for integration with other systems

The system automatically detects students entering through a camera feed, identifies them using face recognition, and records their attendance with timestamps.

---

## Project Structure

```
AAMS_Admin_Panal/
│
├── run.py                     # Entry point (python run.py)
├── wsgi.py                    # WSGI entry (for deployments)
├── app.py                     # Compatibility shim (maps `app` imports)
├── requirements.txt
├── .env                       # Environment variables (DB, secret key, etc.)
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
│   └── utils/
│       ├── camera.py
│       └── helpers.py
```

---

## How Face Recognition Works


### Image Dataset (`image_data/`)

Each student has a dedicated folder under `app/image_data/`:
```
app/image_data/
  Abhiraj/
    img1.jpg
    img2.jpg
    img3.jpg
  Rahul/
    photo1.jpg
    photo2.png
```

**Why multiple images?** 
The system averages the 128-dimensional face encodings from all photos of a student. This makes recognition robust against:
- Lighting changes
- Facial expressions
- Slight pose variations

### Startup Process

1. **Scan**: The `FaceRecognitionService` scans all sub-folders in `image_data/`
2. **Encode**: Each image is processed by `face_recognition.face_encodings()` to extract a 128-d vector
3. **Average**: If a student has 3 photos, the 3 encodings are averaged element-wise
4. **Store**: Averaged encodings are kept in RAM as `known_face_encodings[]` parallel to `known_face_names[]`

### Matching Process (Per Camera Frame)

1. **Detect**: `face_recognition.face_locations()` finds face bounding boxes
2. **Encode**: `face_recognition.face_encodings()` extracts vectors for each face
3. **Compare**: `face_recognition.compare_faces()` checks which known faces are within tolerance (default 0.55)
4. **Best Match**: `face_recognition.face_distance()` finds the closest known face
5. **Log**: If a match is found, the `AttendanceService` records a timestamp in PostgreSQL

### Adding a New Student

1. Create a folder: `mkdir app/image_data/NewStudentName`
2. Add 3-5 clear face photos
3. Call `POST /api/reload-faces` or restart the server

---

## Quick Start

### Prerequisites
- Python 3.7+
- PostgreSQL 14+
- Webcam/Camera
- Modern web browser

### Installation

1. **Clone and navigate**:
```bash
cd attendance-management-system
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
Copy `.env` and fill in your PostgreSQL credentials:
```bash
# .env
SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

4. **Run the application**:
```bash
python run.py
```

5. **Open in browser**:
```
http://localhost:5000
```

---

## Application Factory Pattern

This project uses Flask's **Application Factory** pattern (`app/__init__.py`).

Benefits:
- **Testing**: Create multiple app instances with different configs
- **Blueprints**: Routes are modular and swappable
- **Scaling**: Easy to add Celery workers, CLI commands, or WSGI servers
- **SaaS-ready**: Each tenant could get a configured app instance

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard home |
| `/student-directory` | GET | Student list page |
| `/attendance-logs` | GET | Attendance records page |
| `/reports` | GET | Analytics page |
| `/device-status` | GET | System health page |
| `/video_feed` | GET | MJPEG live camera stream |
| `/api/stats` | GET | Today's dashboard statistics |
| `/api/data` | GET | Recent attendance logs |
| `/api/students` | GET | All registered students |
| `/api/attendance-logs` | GET | All attendance records |
| `/api/attendance-logs/<date>` | GET | Logs by date (YYYY-MM-DD) |
| `/api/weekly-stats` | GET | Weekly breakdown |
| `/api/device-status` | GET | System device status |
| `/api/reload-faces` | POST | Rescan image_data/ folder |

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete request/response schemas.

---

## SaaS Scalability Roadmap

Current architecture is designed for easy scaling:

| Feature | Status | Module |
|---------|--------|--------|
| Modular blueprints | Ready | `app/routes/` |
| Config environments | Ready | `app/config.py` |
| Service layer | Ready | `app/services/` |
| User model scaffold | Ready | `app/models/user.py` |
| JWT Authentication | Planned | `auth_routes.py` |
| SQLAlchemy ORM | Planned | `app/models/` |
| Alembic Migrations | Planned | `app/database/migrations/` |
| Celery Task Queue | Planned | `app/extensions.py` |
| Multi-tenant support | Planned | `app/config.py` |
| Email notifications | Planned | `app/extensions.py` |

---

## Troubleshooting

### Camera not working
- Check camera is connected and not used by another app
- Try changing camera index in `app/utils/camera.py`: `cv2.VideoCapture(0)` → `cv2.VideoCapture(1)`

### Database connection failed
- Verify PostgreSQL is running: `pg_isready -h localhost -p 5432`
- Check `.env` credentials
- Ensure database exists: `createdb attendance_db`

### face_recognition not installed
```bash
pip install face-recognition
```
Note: This requires CMake and dlib compilation. On Windows, use WSL or pre-built wheels.

---

## License

This project is provided as-is for educational and institutional use.

**Version:** 3.0 (Modular Architecture)  
**Framework:** Flask + PostgreSQL + OpenCV + face_recognition  
**Last Updated:** 2026

