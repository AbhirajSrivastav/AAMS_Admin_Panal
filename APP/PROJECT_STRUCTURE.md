AAMS - Attendance Management System
Version 2.0 (Database Integrated)
================================

📁 Project Structure:
====================

attendance-management-system/
│
└── app/
    └── Dashboard/
        │
        ├── 📄 app.py                           # Main Flask application
        ├── 📄 database.py                      # SQLite3 Database Manager
        │
        ├── 📄 Index.html                       # Home dashboard page
        ├── 📄 StudentDirectory.html            # Student list page
        ├── 📄 AttendanceLogs.html              # Attendance records page
        ├── 📄 Reports.html                     # Analytics & reports page
        ├── 📄 DeviceStatus.html                # System status page
        │
        ├── 📄 script.js                        # Frontend JavaScript
        │
        ├── 📁 static/
        │   ├── 📄 style.css                    # Global stylesheet
        │   ├── 📁 css/
        │   ├── 📁 img/
        │   └── 📁 js/
        │
        ├── 📁 templates/
        │   └── 📄 signup.html                  # User signup template
        │
        ├── 📁 instance/                        # Flask instance config
        │
        ├── attendance.db                       # SQLite3 Database (auto-created)
        │
        ├── 📄 requirements.txt                 # Python dependencies
        ├── 📄 API_DOCUMENTATION.md             # API Reference
        └── 📄 README.md                        # Project documentation


DATABASE STRUCTURE:
===================

SQLite3 Database: attendance.db

Tables:
  1. students
     - id (INTEGER PRIMARY KEY)
     - name (TEXT UNIQUE)
     - student_id (TEXT UNIQUE)
     - email (TEXT UNIQUE)
     - phone (TEXT)
     - status (TEXT)
     - created_at (TIMESTAMP)

  2. attendance_logs
     - id (INTEGER PRIMARY KEY)
     - student_id (INTEGER FK)
     - check_in_time (TIMESTAMP)
     - check_out_time (TIMESTAMP)
     - date (DATE)
     - status (TEXT)
     - notes (TEXT)

  3. daily_stats
     - id (INTEGER PRIMARY KEY)
     - date (DATE UNIQUE)
     - total_students (INTEGER)
     - present (INTEGER)
     - absent (INTEGER)
     - late (INTEGER)
     - created_at (TIMESTAMP)

  4. device_status
     - id (INTEGER PRIMARY KEY)
     - device_name (TEXT UNIQUE)
     - status (TEXT)
     - last_seen (TIMESTAMP)
     - uptime_seconds (INTEGER)
     - details (TEXT)


KEY FILES:
==========

📄 app.py
  - Flask server initialization
  - Video streaming endpoint
  - REST API endpoints
  - Camera integration with face detection
  - Automatic attendance logging

📄 database.py
  - SQLite3 connection management
  - CRUD operations for all tables
  - Statistical queries
  - Device status management
  - Sample data initialization

📄 Index.html
  - Dashboard homepage
  - Live camera feed display
  - Weekly attendance trends chart
  - Real-time statistics
  - Activity feed

📄 script.js
  - Real-time clock
  - Chart.js integration
  - API calls to backend
  - Dynamic UI updates
  - Multi-period attendance view (Week/Month/Year)

📄 style.css
  - Dark theme styling
  - Responsive design
  - Color variables
  - Component styling


RUNNING THE APPLICATION:
========================

1. Install dependencies:
   pip install -r requirements.txt

2. Run the Flask server:
   python app.py

3. Open in browser:
   http://localhost:5000

4. Navigate pages:
   - Home: Dashboard with charts
   - Student Directory: List all students
   - Attendance Logs: View attendance records
   - Reports: Analytics and statistics
   - Device Status: System health monitoring


API ENDPOINTS:
==============

Dashboard:
  GET /api/stats                 - Get daily statistics
  GET /api/data                  - Get attendance records
  GET /video_feed                - Live video stream

Students:
  GET /api/students              - Get all students

Attendance:
  GET /api/attendance-logs       - Get all logs
  GET /api/attendance-logs/<date> - Get logs by date

Statistics:
  GET /api/weekly-stats          - Get weekly breakdown

Device:
  GET /api/device-status         - Get device status


FEATURES:
=========

✅ Real-time Video Feed
   - Live camera stream from main entrance
   - Face detection using OpenCV
   - Automatic attendence logging

✅ Database Integration
   - SQLite3 persistent storage
   - Automatic backups possible
   - Efficient queries
   - Referential integrity

✅ Dashboard
   - Real-time attendance statistics
   - Weekly/Monthly/Yearly trends
   - Live update of analytics

✅ Student Management
   - View all registered students
   - Search functionality
   - Student details

✅ Attendance Logs
   - View daily attendance records
   - Date filtering
   - Status tracking (Present/Absent/Late)

✅ Reports
   - Weekly attendance distribution
   - Attendance rate calculations
   - Visual charts and graphs

✅ Device Status
   - Camera status
   - AI model status
   - Database status
   - Server status
   - System event logs


DEPENDENCIES:
=============

Flask              - Web framework
OpenCV             - Video processing & face detection
Pandas             - Data manipulation
SQLite3            - Database (built-in Python)
Chart.js           - Frontend charting library
Font Awesome       - Icon library


SAMPLE DATA:
============

Pre-populated students:
  1. Abhiraj Srivastava (STU001)
  2. Rahul Sharma (STU002)
  3. Sanya Malhotra (STU003)
  4. Vikram Singh (STU004)
  5. Anjali Rao (STU005)
  6. Arya Panday (STU006)

Sample attendance logs for today with realistic times and status.


TROUBLESHOOTING:
================

Camera not working:
  - Check camera permissions
  - Try: cv2.VideoCapture(0 or 1)
  - Run: ls /dev/video* (Linux)

Database errors:
  - Delete attendance.db to reset
  - Check file permissions
  - Ensure SQLite3 installed

API not responding:
  - Check Flask server status
  - Review app.py logs
  - Verify database connection

Port conflict:
  - Change port in app.py: app.run(port=5001)


FUTURE ENHANCEMENTS:
====================

□ Real face recognition (Deep Learning)
□ Email notifications
□ Mobile app
□ Advanced analytics
□ Biometric integration
□ QR code attendance
□ SMS alerts
□ Report generation (PDF/Excel)
□ User authentication
□ Multi-campus support
