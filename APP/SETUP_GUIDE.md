# AAMS Setup Guide - Complete Installation & Configuration

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Webcam/Camera (for video feed)
- Modern web browser

---

## Installation Steps

### 1. Clone or Download Project

```bash
cd c:\Users\Admin\Desktop\attendance-management-system\app\Dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- Flask (web server)
- OpenCV (video processing)
- Pandas (data handling)
- SQLite3 support (included in Python)

### 3. Initialize Database

The database is automatically created on first run. It will:
- Create `attendance.db` with all tables
- Insert 6 sample students
- Insert sample attendance records
- Initialize device status entries

### 4. Run the Application

```bash
python app.py
```

**Output:**
```
WARNING in app.run_simple
  * Running on http://127.0.0.1:5000
  * Debug mode: on
  * Press CTRL+C to quit
```

### 5. Open in Browser

Visit: `http://localhost:5000`

You should see the AAMS Dashboard!

---

## Database Integration Guide

### How SQLite3 Works

SQLite3 is a file-based database - no server needed:
- **File**: `attendance.db` (created automatically)
- **Size**: Starts small, grows with data
- **Backup**: Simply copy the file

### Database Manager Class

The `database.py` file contains the `DatabaseManager` class that handles:

```python
from database import DatabaseManager

# Initialize database
db = DatabaseManager('attendance.db')

# Add a student
db.add_student('John Doe', 'STU123', 'john@school.com', '1234567890')

# Log attendance
db.add_attendance('John Doe', '2026-02-17 09:15:00', 'Present', 'Face detected')

# Get statistics
stats = db.get_attendance_stats()
print(stats)  # {'total_students': 285, 'present_today': 250, ...}
```

### Sample Data

Default students in database:
1. Abhiraj Srivastava (STU001)
2. Rahul Sharma (STU002)
3. Sanya Malhotra (STU003)
4. Vikram Singh (STU004)
5. Anjali Rao (STU005)
6. Arya Panday (STU006)

### Auto-Logging with Camera

When faces are detected by the camera:
1. OpenCV detects the face
2. System picks a random student (demo mode)
3. Attendance record is created
4. Record is saved to database
5. Dashboard updates in real-time

---

## File Descriptions

### Core Files

**app.py** (Flask Backend)
- Routes for all pages
- Video streaming
- API endpoints
- Camera integration
- Database initialization

**database.py** (Database Manager)
- SQLite3 connection
- CRUD operations
- Statistical queries
- Device status tracking

### HTML Pages

**Index.html** (Home/Dashboard)
- Real-time clock
- Live camera feed
- Weekly attendance chart
- Statistics cards
- Activity feed

**StudentDirectory.html**
- List of all students
- Search functionality
- Status indicators (Present/Absent/Late)

**AttendanceLogs.html**
- Attendance records
- Date filtering
- Detailed logs

**Reports.html**
- Weekly charts
- Attendance distribution
- Monthly trends
- Attendance rate

**DeviceStatus.html**
- System monitoring
- Device health
- Event logs
- Performance metrics

### Frontend Files

**script.js**
- Real-time clock
- Chart.js integration
- API communication
- Dynamic updates
- Multi-period view (Week/Month/Year)

**style.css**
- Dark theme (CSS variables)
- Responsive layout
- Component styling
- Color scheme

---

## Configuration

### Change Server Port

Edit `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port here
```

### Camera Selection

Edit `app.py` `generate_frames()` function:
```python
# Try different camera indices
camera = cv2.VideoCapture(0)  # 0 = default, 1 = external USB camera
```

### Database Location

Edit path in `app.py`:
```python
db = DatabaseManager(os.path.join(current_dir, 'custom_location/attendance.db'))
```

---

## API Usage

### Getting Data from API

**Get Today's Statistics:**
```javascript
fetch('/api/stats')
    .then(r => r.json())
    .then(data => {
        console.log(`Present: ${data.present_today}`);
        console.log(`Attendance Rate: ${data.attendance_rate}%`);
    });
```

**Get All Students:**
```javascript
fetch('/api/students')
    .then(r => r.json())
    .then(students => {
        students.forEach(s => {
            console.log(`${s.name} (${s.student_id})`);
        });
    });
```

**Get Attendance Logs:**
```javascript
fetch('/api/attendance-logs')
    .then(r => r.json())
    .then(logs => {
        logs.forEach(log => {
            console.log(`${log.student_name}: ${log.status}`);
        });
    });
```

---

## Database Operations

### Python Usage

```python
from database import DatabaseManager

db = DatabaseManager()

# Get all students
students = db.get_all_students()
for s in students:
    print(s['name'], s['email'])

# Add new student
db.add_student('Jane Doe', 'STU999', 'jane@school.com', '1234567890')

# Log attendance
db.add_attendance('Jane Doe', '2026-02-17 09:30:00', 'Present', 'Face detected')

# Get statistics
stats = db.get_attendance_stats()
print(f"Attendance Rate: {stats['attendance_rate']}%")

# Get weekly data
weekly = db.get_weekly_stats()
for day in weekly:
    print(f"{day['date']}: {day['present']} present")

# Get device status
devices = db.get_device_status()
for device in devices:
    print(f"{device['device_name']}: {device['status']}")
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'cv2'"

**Solution:**
```bash
pip install opencv-python
```

### Issue: "Can't open camera (Camera Not Available)"

**Solutions:**
- Check camera is connected
- Check camera permissions (Linux: `sudo chmod 666 /dev/video0`)
- Try different camera index (0, 1, 2)
- Restart camera service

### Issue: "Database locked"

**Solutions:**
- Close other connections to database
- Restart Flask server
- Delete `attendance.db-journal` file if exists

### Issue: "Port 5000 already in use"

**Solution:**
- Kill process using port: `taskkill /pid <PID> /f` (Windows)
- Or change port in `app.py`

### Issue: "No student data showing"

**Solutions:**
- Check database is initialized
- Verify sample data was inserted
- Check database file exists: `ls attendance.db`
- Reset database: delete `attendance.db` and restart

---

## Backup & Recovery

### Backup Database

```bash
# Windows
copy attendance.db attendance.db.backup

# Linux/Mac
cp attendance.db attendance.db.backup
```

### Restore from Backup

```bash
# Windows
copy attendance.db.backup attendance.db

# Linux/Mac
cp attendance.db.backup attendance.db
```

### Reset Database

Simply delete the file - it will be recreated automatically:
```bash
del attendance.db  # Windows
rm attendance.db   # Linux/Mac
```

---

## Performance Tips

1. **Large Datasets**
   - Add database indexes for faster queries
   - Archive old records regularly

2. **Camera Feed**
   - Reduce resolution for faster processing
   - Adjust face detection parameters

3. **Multiple Users**
   - Add authentication layer
   - Implement user roles

---

## Advanced Configuration

### Add Custom Student

```python
db.add_student('John Smith', 'STU100', 'john@school.com', '9876543210')
```

### Bulk Import Students

```python
import csv

with open('students.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        db.add_student(
            row['name'],
            row['student_id'],
            row['email'],
            row['phone']
        )
```

### Export Attendance to CSV

```python
import csv

logs = db.get_all_attendance_logs(limit=1000)

with open('attendance_export.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=logs[0].keys())
    writer.writeheader()
    writer.writerows(logs)
```

---

## Production Deployment

For production use, consider:

1. **Security**
   - Add authentication
   - Use HTTPS
   - Implement API key validation

2. **Database**
   - Use PostgreSQL/MySQL
   - Set up automatic backups
   - Enable database encryption

3. **Server**
   - Use production WSGI server (Gunicorn)
   - Set up reverse proxy (Nginx)
   - Configure SSL certificates

4. **Monitoring**
   - Set up logging
   - Monitor database size
   - Track API performance

---

## Support

For issues or questions:
1. Check API_DOCUMENTATION.md
2. Review PROJECT_STRUCTURE.md
3. Check application logs
4. Verify database connection

---

Happy Attendance Tracking! 🎓
