# AAMS - Attendance Management System v2.0

**Advanced Face Recognition Based Attendance Management System with SQLite3 Database Integration**

![Python](https://img.shields.io/badge/Python-3.7+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)
![SQLite3](https://img.shields.io/badge/SQLite3-Built--in-lightblue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-red)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 🎯 Overview

AAMS (Attendance Management System) is a comprehensive solution that combines:
- **Real-time video processing** with face detection
- **Automatic attendance logging** to SQLite3 database
- **Interactive dashboard** with live analytics
- **Multi-page web interface** for student & attendance management
- **RESTful API** for integration with other systems

The system automatically detects students entering through a camera feed and records their attendance with timestamps, status (Present/Absent/Late), and notes.

---

## ✨ Key Features

### 🎥 Video Processing
- Real-time camera feed with face detection
- OpenCV powered face recognition
- Automatic attendance logging when faces detected
- Live overlay with detection status

### 📊 Dashboard
- Real-time attendance statistics
- Weekly/Monthly/Yearly attendance trends
- Interactive Chart.js graphs
- Live activity feed
- Responsive dark theme UI

### 📁 Student Management
- Complete student directory
- Search functionality
- Individual student profiles
- Attendance history per student

### 📋 Attendance Logs
- Daily attendance records
- Date filtering
- Status tracking (Present/Absent/Late)
- Detailed notes for each record

### 📈 Reports & Analytics
- Weekly distribution charts
- Attendance rate calculations
- Trend analysis
- Performance metrics

### ⚙️ Device Monitoring
- System health status
- Device connectivity check
- Event logs
- Uptime tracking

### 🗄️ Database Integration
- SQLite3 persistent storage
- 4 optimized tables (students, attendance_logs, daily_stats, device_status)
- Automatic schema creation
- Sample data pre-population

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.7+
Webcam/Camera (for video feed)
Modern web browser
```

### Installation

1. **Navigate to project directory:**
```bash
cd attendance-management-system/app/Dashboard
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

4. **Open in browser:**
```
http://localhost:5000
```

That's it! The database will be created automatically with sample data.

---

## 📚 Project Structure

```
Dashboard/
├── app.py                          # Flask backend
├── database.py                     # SQLite3 manager
├── Index.html                      # Home dashboard
├── StudentDirectory.html           # Student list
├── AttendanceLogs.html            # Attendance records
├── Reports.html                    # Analytics
├── DeviceStatus.html              # System monitoring
├── script.js                       # Frontend logic
├── static/
│   └── style.css                  # Styling
└── attendance.db                   # SQLite3 database (auto-created)
```

---

## 🔌 API Endpoints

### Dashboard
- `GET /api/stats` - Daily statistics
- `GET /api/data` - Attendance records
- `GET /video_feed` - Live video stream

### Students
- `GET /api/students` - All students

### Attendance
- `GET /api/attendance-logs` - All logs
- `GET /api/attendance-logs/<date>` - Logs by date

### Statistics
- `GET /api/weekly-stats` - Weekly breakdown

### Device Status
- `GET /api/device-status` - System status

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete details.

---

## 🗄️ Database Schema

### Students Table
```sql
- id (INTEGER PRIMARY KEY)
- name (TEXT UNIQUE)
- student_id (TEXT UNIQUE)
- email (TEXT UNIQUE)
- phone (TEXT)
- status (TEXT)
- created_at (TIMESTAMP)
```

### Attendance Logs Table
```sql
- id (INTEGER PRIMARY KEY)
- student_id (INTEGER FK)
- check_in_time (TIMESTAMP)
- check_out_time (TIMESTAMP)
- date (DATE)
- status (TEXT: Present/Absent/Late)
- notes (TEXT)
```

### Daily Stats Table
```sql
- date (DATE)
- total_students (INTEGER)
- present (INTEGER)
- absent (INTEGER)
- late (INTEGER)
```

### Device Status Table
```sql
- device_name (TEXT UNIQUE)
- status (TEXT: Active/Inactive)
- last_seen (TIMESTAMP)
- details (TEXT)
```

---

## 💻 Usage Examples

### Python Backend
```python
from database import DatabaseManager

db = DatabaseManager()

# Get statistics
stats = db.get_attendance_stats()
print(f"Present today: {stats['present_today']}")

# Add student
db.add_student('John Doe', 'STU123', 'john@school.com')

# Log attendance
db.add_attendance('John Doe', '2026-02-17 09:15:00', 'Present')

# Get weekly data
weekly = db.get_weekly_stats()
```

### JavaScript Frontend
```javascript
// Get statistics
fetch('/api/stats')
    .then(r => r.json())
    .then(data => {
        console.log(`Attendance Rate: ${data.attendance_rate}%`);
    });

// Get students
fetch('/api/students')
    .then(r => r.json())
    .then(students => console.log(students));
```

---

## 🎨 UI Features

### Dashboard
- Real-time clock with HH:MM:SS format
- Live camera feed display
- 4 stats cards (Total Students, Present, Absent, Late)
- Week/Month/Year toggle for attendance trends
- Statistics panel showing averages
- Activity feed with auto-refresh

### Navigation
- Sidebar navigation to all pages
- Active page highlighting
- Responsive mobile-friendly design
- Dark theme with green accents

### Dark Theme Colors
- Background: `#121826`
- Sidebar: `#1c2536`
- Cards: `#1e293b`
- Primary Green: `#22c55e`
- Secondary Blue: `#38bdf8`
- Error Red: `#ef4444`
- Warning Orange: `#f59e0b`

---

## 🔧 Configuration

### Change Server Port
Edit `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

### Database Location
Edit `app.py`:
```python
db = DatabaseManager('custom_path/attendance.db')
```

### Camera Selection
Edit `app.py`:
```python
camera = cv2.VideoCapture(1)  # Use different index
```

---

## 📦 Dependencies

```
Flask==2.3.3              # Web framework
pandas==2.0.3            # Data handling
opencv-python==4.8.0.74  # Video processing
numpy==1.24.3            # Scientific computing
Werkzeug==2.3.7          # WSGI utilities
```

All included in `requirements.txt`

---

## 🐛 Troubleshooting

### Camera not working
```bash
# Check camera device
ls /dev/video*  # Linux
# Try different index in cv2.VideoCapture()
```

### Port already in use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :5000   # Windows
```

### Database locked
```bash
# Reset database
rm attendance.db
# Restart Flask server
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more help.

---

## 📋 Sample Data

Pre-loaded students:
1. **Abhiraj Srivastava** (STU001) - abhiraj@school.com
2. **Rahul Sharma** (STU002) - rahul@school.com
3. **Sanya Malhotra** (STU003) - sanya@school.com
4. **Vikram Singh** (STU004) - vikram@school.com
5. **Anjali Rao** (STU005) - anjali@school.com
6. **Arya Panday** (STU006) - arya@school.com

Sample attendance records for today automatically generated.

---

## 📊 Dashboard Pages

### 🏠 Home
- Live camera feed
- Weekly attendance trends
- Today's statistics
- Recent activity

### 👥 Student Directory
- Complete student list
- Search functionality
- Student info (ID, Email, Status)
- Last seen timestamp

### 📝 Attendance Logs
- Daily attendance records
- Date filtering
- Status indicators
- Detailed notes

### 📈 Reports
- Weekly distribution chart
- Attendance by status (pie chart)
- Monthly trend analysis
- Summary statistics

### ⚙️ Device Status
- Camera health
- AI model status
- Database info
- Server status
- System event logs

---

## 🔒 Security Considerations

For production deployment:
- Add user authentication
- Implement API key validation
- Use HTTPS/SSL
- Add rate limiting
- Implement input validation
- Use environment variables for config

---

## 🚀 Future Enhancements

- [ ] Real face recognition (Deep Learning models)
- [ ] Email/SMS notifications
- [ ] Mobile app
- [ ] Advanced analytics & reports
- [ ] Biometric integration
- [ ] QR code attendance
- [ ] Report generation (PDF/Excel)
- [ ] Multi-campus support
- [ ] Attendance policies
- [ ] Holiday management

---

## 📞 Support & Documentation

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project organization
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions

---

## 📄 License

This project is provided as-is for educational and institutional use.

---

## 👨‍💻 Development Info

**Version:** 2.0  
**Last Updated:** February 17, 2026  
**Database:** SQLite3  
**Framework:** Flask  
**Frontend:** HTML/CSS/JavaScript  
**Video Processing:** OpenCV  

---

## 🎓 Built With

- **Python** - Backend logic
- **Flask** - Web framework
- **SQLite3** - Database
- **OpenCV** - Face detection
- **Chart.js** - Data visualization
- **Font Awesome** - Icons
- **HTML/CSS/JavaScript** - Frontend

---

## 💡 Key Highlights

✅ **Zero Configuration** - Works out of the box  
✅ **Auto Database** - SQLite3 created automatically  
✅ **Face Detection** - OpenCV powered  
✅ **Real-time Updates** - Live statistics  
✅ **Responsive Design** - Mobile friendly  
✅ **RESTful API** - Easy integration  
✅ **Sample Data** - Pre-loaded for demo  
✅ **Dark Theme** - Eye-friendly UI  

---

## 🙏 Acknowledgments

Built with Python, Flask, OpenCV, and Chart.js

---

**Start tracking attendance automatically today! 📊✨**

For more information, see [SETUP_GUIDE.md](SETUP_GUIDE.md)
