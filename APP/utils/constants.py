"""
app/utils/constants.py
======================
Centralized constants for the Attendance Management System.

Keeping magic numbers, strings, and enums in one place makes the
app easier to maintain and safer to modify. It also simplifies
future SaaS multi-tenant customizations.
"""

from enum import Enum


class StudentStatus(str, Enum):
    """Allowed values for the students.status column."""
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'


class AttendanceStatus(str, Enum):
    """Allowed values for the attendance_logs.status column."""
    PRESENT = 'Present'
    ABSENT = 'Absent'
    LATE = 'Late'


class DeviceStatus(str, Enum):
    """Allowed values for the device_status.status column."""
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    ERROR = 'Error'
    MAINTENANCE = 'Maintenance'


# File-system constants
VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

# Face recognition constants
DEFAULT_FACE_TOLERANCE = 0.55
DEFAULT_LATE_HOUR = 10
DEFAULT_LATE_MINUTE = 0
LOG_THROTTLE_SECONDS = 2
DETECTED_FACE_CACHE_TTL = 60  # seconds before removing stale face tracking entries

# Camera constants
DEFAULT_CAMERA_INDEX = 0
MJPEG_FRAME_RATE = 30          # Target FPS for stream
FRAME_SLEEP_INTERVAL = 0.03  # seconds between frame yields (~33 FPS)
PLACEHOLDER_WIDTH = 640
PLACEHOLDER_HEIGHT = 480

# Route names (useful for url_for generation)
ROUTE_INDEX = 'dashboard.index'
ROUTE_STUDENT_DIRECTORY = 'student.student_directory'
ROUTE_ATTENDANCE_LOGS = 'attendance.attendance_logs'
ROUTE_REPORTS = 'dashboard.reports'
ROUTE_DEVICE_STATUS = 'dashboard.device_status'

