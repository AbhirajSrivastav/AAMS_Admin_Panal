# AAMS API Documentation v3.0

## Base URL
```
http://localhost:5000
```

## Authentication
Currently, the system runs in single-admin mode. Authentication endpoints
are scaffolded in `app/routes/auth_routes.py` for future JWT or session-based auth.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SECRET_KEY | dev-secret-key | Flask session encryption key |
| DB_HOST | localhost | PostgreSQL server host |
| DB_NAME | attendance_db | Database name |
| DB_USER | postgres | Database user |
| DB_PASSWORD | (empty) | User password |
| DB_PORT | 5432 | Server port |
| FACE_TOLERANCE | 0.55 | Face matching strictness (lower = stricter) |
| IMAGE_DATA_DIR | app/image_data | Student face images folder |

---

## REST API Endpoints

### Dashboard

#### Get Dashboard Statistics
```
GET /api/stats
```
Returns today's attendance KPIs.

```json
{
    "total_students": 285,
    "present_today": 250,
    "absent_today": 35,
    "late_today": 15,
    "attendance_rate": 97.9
}
```

#### Get Attendance Data
```
GET /api/data?limit=100
```
Returns recent attendance records with student names joined.

```json
[
    {
        "id": 1,
        "student_id": 1,
        "student_name": "Abhiraj Srivastava",
        "check_in_time": "2026-02-17 09:15:00",
        "date": "2026-02-17",
        "status": "Present",
        "notes": "Face detected"
    }
]
```

#### Get Weekly Statistics
```
GET /api/weekly-stats?offset=0
```
Returns daily breakdown for a 7-day window.

```json
[
    {
        "date": "2026-02-17",
        "present": 275,
        "absent": 8,
        "late": 2
    }
]
```

---

### Students

#### Get All Students
```
GET /api/students
```

```json
[
    {
        "id": 1,
        "name": "Abhiraj Srivastava",
        "student_id": "STU001",
        "email": "abhiraj@school.com",
        "phone": "9876543210",
        "status": "Active",
        "created_at": "2026-02-17T07:00:00"
    }
]
```

#### Reload Face Encodings
```
POST /api/reload-faces
```
Rescans the `image_data/` folder and reloads all face encodings.
Use this after adding new student photos without restarting the server.

```json
{
    "status": "ok",
    "students_loaded": 6,
    "students": ["Abhiraj", "Rahul", "Sanya", "Vikram", "Anjali", "Arya"]
}
```

---

### Attendance Logs

#### Get All Logs
```
GET /api/attendance-logs?limit=50
```

```json
[
    {
        "id": 1,
        "student_id": 1,
        "student_name": "Abhiraj Srivastava",
        "check_in_time": "2026-02-17 09:15:00",
        "date": "2026-02-17",
        "status": "Present",
        "notes": "Face detected"
    }
]
```

#### Get Logs by Date
```
GET /api/attendance-logs/2026-02-17
```

---

### Device Status

#### Get All Device Status
```
GET /api/device-status
```

```json
[
    {
        "id": 1,
        "device_name": "Camera",
        "status": "Active",
        "last_seen": "2026-02-17T10:15:30",
        "uptime_seconds": 31500,
        "details": "Main entrance camera - ready"
    }
]
```

---

## Video Streaming

```
GET /video_feed
```
Returns MJPEG stream:
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- Frame rate: ~30 FPS
- Resolution: Device default (typically 640x480 or 1920x1080)

---

## Face Recognition System

### How image_data is used
The `FaceRecognitionService` (in `app/services/face_recognition_service.py`) 
performs the following at startup:

1. Scan `app/image_data/` for sub-folders (one per student)
2. Load all `.jpg/.jpeg/.png/.bmp/.webp` images
3. Extract 128-d face encodings via `face_recognition.face_encodings()`
4. Average multiple encodings per student for robustness
5. Store in memory for real-time matching

### How to add new student images
```bash
# 1. Create folder
mkdir app/image_data/new_student_name

# 2. Add photos
cp photo1.jpg app/image_data/new_student_name/
cp photo2.jpg app/image_data/new_student_name/

# 3. Reload without restart
curl -X POST http://localhost:5000/api/reload-faces
```

### Matching algorithm
1. Convert OpenCV BGR frame to RGB
2. `face_locations()` → detect all faces
3. `face_encodings()` → extract 128-d vectors
4. `compare_faces()` → boolean matches within tolerance
5. `face_distance()` → find closest match
6. Log attendance if best match < tolerance

---

## Database Schema

### Students
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PRIMARY KEY |
| name | TEXT | NOT NULL, UNIQUE |
| student_id | TEXT | NOT NULL, UNIQUE |
| email | TEXT | NOT NULL, UNIQUE |
| phone | TEXT | |
| status | TEXT | DEFAULT 'Active' |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### Attendance Logs
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PRIMARY KEY |
| student_id | INTEGER | FK → students(id) |
| check_in_time | TIMESTAMP | NOT NULL |
| check_out_time | TIMESTAMP | |
| date | DATE | NOT NULL |
| status | TEXT | NOT NULL |
| notes | TEXT | |
| UNIQUE | (student_id, date) | |

### Daily Stats
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PRIMARY KEY |
| date | DATE | UNIQUE |
| total_students | INTEGER | DEFAULT 0 |
| present | INTEGER | DEFAULT 0 |
| absent | INTEGER | DEFAULT 0 |
| late | INTEGER | DEFAULT 0 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### Device Status
| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PRIMARY KEY |
| device_name | TEXT | UNIQUE |
| status | TEXT | DEFAULT 'Active' |
| last_seen | TIMESTAMP | |
| uptime_seconds | INTEGER | DEFAULT 0 |
| details | TEXT | |

---

## Error Responses

All API errors return JSON with a descriptive message:

```json
{
    "error": "Camera not available",
    "message": "Could not open video capture device"
}
```

Common HTTP status codes:
- `200 OK` — Success
- `404 Not Found` — Resource does not exist
- `500 Internal Server Error` — Database or camera error

