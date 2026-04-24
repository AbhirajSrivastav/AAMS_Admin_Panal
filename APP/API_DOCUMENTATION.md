# AAMS API Documentation

## Database Integration
The system now uses **SQLite3** for persistent data storage. All data is stored in `attendance.db` with the following tables:

### Database Tables

#### 1. Students Table
Stores student information
```sql
- id: INTEGER PRIMARY KEY
- name: TEXT (unique)
- student_id: TEXT (unique)
- email: TEXT (unique)
- phone: TEXT
- status: TEXT (Active/Inactive)
- created_at: TIMESTAMP
```

#### 2. Attendance Logs Table
Records daily attendance
```sql
- id: INTEGER PRIMARY KEY
- student_id: INTEGER FK (students.id)
- check_in_time: TIMESTAMP
- check_out_time: TIMESTAMP (nullable)
- date: DATE
- status: TEXT (Present/Absent/Late)
- notes: TEXT
- Unique constraint on (student_id, date)
```

#### 3. Daily Stats Table
Pre-calculated daily statistics
```sql
- id: INTEGER PRIMARY KEY
- date: DATE (unique)
- total_students: INTEGER
- present: INTEGER
- absent: INTEGER
- late: INTEGER
- created_at: TIMESTAMP
```

#### 4. Device Status Table
Monitors system components
```sql
- id: INTEGER PRIMARY KEY
- device_name: TEXT (unique)
- status: TEXT (Active/Inactive)
- last_seen: TIMESTAMP
- uptime_seconds: INTEGER
- details: TEXT
```

---

## REST API Endpoints

### Dashboard API

#### Get Dashboard Statistics
```
GET /api/stats
```
Returns overall attendance statistics for the current day.
```json
Response:
{
    "total_students": 285,
    "present_today": 250,
    "absent_today": 35,
    "late_today": 15,
    "attendance_rate": 97.9
}
```

#### Get All Attendance Data
```
GET /api/data
```
Returns latest 100 attendance records with student names.
```json
Response: [
    {
        "id": 1,
        "student_id": 1,
        "student_name": "Abhiraj Srivastava",
        "check_in_time": "2026-02-17 09:15:00",
        "date": "2026-02-17",
        "status": "Present",
        "notes": "Face detected"
    },
    ...
]
```

---

### Student Management API

#### Get All Students
```
GET /api/students
```
Returns list of all registered students.
```json
Response: [
    {
        "id": 1,
        "name": "Abhiraj Srivastava",
        "student_id": "STU001",
        "email": "abhiraj@school.com",
        "phone": "9876543210",
        "status": "Active",
        "created_at": "2026-02-17 07:00:00"
    },
    ...
]
```

---

### Attendance Logs API

#### Get All Attendance Logs
```
GET /api/attendance-logs
```
Returns all attendance records.
```json
Response: [
    {
        "id": 1,
        "student_id": 1,
        "student_name": "Abhiraj Srivastava",
        "check_in_time": "2026-02-17 09:15:00",
        "date": "2026-02-17",
        "status": "Present",
        "notes": "Face detected"
    },
    ...
]
```

#### Get Attendance by Date
```
GET /api/attendance-logs/<date>
```
Parameters:
- `date` (string): Date in format YYYY-MM-DD

```json
Response: [
    {
        "id": 1,
        "student_id": 1,
        "student_name": "Abhiraj Srivastava",
        "check_in_time": "2026-02-17 09:15:00",
        "date": "2026-02-17",
        "status": "Present",
        "notes": "Face detected"
    },
    ...
]
```

---

### Statistics API

#### Get Weekly Statistics
```
GET /api/weekly-stats
```
Returns daily breakdown for the current week.
```json
Response: [
    {
        "date": "2026-02-17",
        "present": 275,
        "absent": 8,
        "late": 2
    },
    ...
]
```

---

### Device Status API

#### Get Device Status
```
GET /api/device-status
```
Returns status of all system devices.
```json
Response: [
    {
        "id": 1,
        "device_name": "Camera",
        "status": "Active",
        "last_seen": "2026-02-17 10:15:30",
        "uptime_seconds": 31500,
        "details": "Main entrance camera - ready"
    },
    {
        "id": 2,
        "device_name": "Face Recognition AI",
        "status": "Active",
        "last_seen": "2026-02-17 10:15:30",
        "uptime_seconds": 31500,
        "details": "TensorFlow model - ready"
    },
    ...
]
```

---

## Video Streaming

#### Get Live Video Feed
```
GET /video_feed
```
Returns real-time video stream from camera in MJPEG format.
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- Frame rate: 30 FPS
- Resolution: 1920x1080 (or device default)

---

## Database Methods (Python)

### DatabaseManager Class

#### Student Operations
```python
db.get_all_students()              # Returns all students
db.get_student(student_id)         # Get specific student
db.add_student(name, id, email)    # Add new student
db.update_student(id, **kwargs)    # Update student info
```

#### Attendance Operations
```python
db.get_all_attendance_logs(limit)  # Get attendance records
db.get_attendance_by_date(date)    # Get logs for specific date
db.get_student_attendance(sid)     # Get student's history
db.add_attendance(name, time, status, notes)  # Log attendance
```

#### Statistics
```python
db.get_daily_stats(date)           # Daily statistics
db.get_weekly_stats(week_offset)   # Weekly breakdown
db.get_attendance_stats()          # Overall statistics
db.get_unique_faces_count()        # Count unique students
```

#### Device Status
```python
db.update_device_status(name, status, details)
db.get_device_status(device_name)  # Get specific device
db.get_device_status()             # Get all devices
```

---

## Sample Usage

### Python (Flask Backend)
```python
from database import DatabaseManager

db = DatabaseManager('attendance.db')

# Get all students
students = db.get_all_students()

# Add attendance
db.add_attendance('Abhiraj Srivastava', '2026-02-17 09:15:00', 'Present', 'Face detected')

# Get today's stats
stats = db.get_attendance_stats()
print(f"Present today: {stats['present_today']}")
```

### JavaScript (Frontend)
```javascript
// Fetch all students
fetch('/api/students')
    .then(response => response.json())
    .then(data => {
        console.log('Students:', data);
    });

// Fetch today's stats
fetch('/api/stats')
    .then(response => response.json())
    .then(data => {
        document.getElementById('total-count').innerText = data.present_today;
    });
```

---

## Data Persistence

All data is automatically saved to SQLite database:
- **Location**: `attendance.db` (same directory as app.py)
- **Size**: Grows ~0.5MB per 1000 attendance records
- **Backup**: Regular backups recommended

To backup database:
```bash
cp attendance.db attendance.db.backup
```

---

## Notes

- All timestamps are in UTC/IST format
- Attendance records are unique per (student_id, date) combination
- API responses include all related information (student names with logs)
- Device status is automatically updated on system startup
- Camera detection limits to 1 record per face every 2 seconds to prevent duplicates
