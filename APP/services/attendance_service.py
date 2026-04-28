"""
app/services/attendance_service.py
===================================
Attendance Service: business logic for logging and managing attendance.

This layer sits between the database (data persistence) and the routes
(HTTP handlers). It enforces business rules such as:
    - Throttling: one log per student per 2-second window (prevents duplicates)
    - Auto-registration: if a recognized face has no DB record, create one
    - Status determination: Present vs Late based on time thresholds
    - Graceful degradation: works even when face_recognition is unavailable
"""

import re
import datetime
from typing import Optional
from app.database.db import DatabaseManager


class AttendanceService:
    """
    Handles all attendance-related business operations.

    Usage:
        service = AttendanceService()
        service.mark_attendance('Abhiraj Srivastava')
    """

    # Time threshold: arrivals after 10:00 AM are marked "Late"
    LATE_HOUR = 10
    LATE_MINUTE = 0

    # Throttle window: seconds between duplicate logs for the same face
    LOG_THROTTLE_SECONDS = 2

    def __init__(self, db: DatabaseManager = None):
        """
        Initialize the service.

        Args:
            db (DatabaseManager): Existing DB instance, or None to create new.
        """
        self.db = db or DatabaseManager()
        # Track recently logged faces to prevent duplicate entries
        # Key: face identifier string, Value: datetime of last log
        self._recent_logs = {}

    # ------------------------------------------------------------------
    # Core attendance logic
    # ------------------------------------------------------------------

    def mark_attendance(self, student_name: str, notes: str = 'Face recognized via camera') -> bool:
        """
        Log attendance for a recognized student with throttling.

        Business rules applied:
            1. Look up the student by name in the database.
            2. If not found, auto-create a new student record.
            3. Throttle: skip if this student was already logged within
               the last LOG_THROTTLE_SECONDS seconds.
            4. Determine status (Present or Late) based on current time.
            5. Insert attendance record via DatabaseManager.

        Args:
            student_name (str): Name returned by face recognition.
            notes (str): Optional note for the log entry.

        Returns:
            bool: True if a new attendance record was created, False if
                  throttled or an error occurred.
        """
        # 1. Ensure student exists in database
        student = self.db.get_student_by_name(student_name)
        if not student:
            self._auto_register_student(student_name)

        # 2. Throttle check
        now = datetime.datetime.now()
        last_log = self._recent_logs.get(student_name)
        if last_log and (now - last_log).seconds < self.LOG_THROTTLE_SECONDS:
            return False  # too soon, skip

        # 3. Determine Present / Late status
        status = self._determine_status(now)

        # 4. Format timestamp
        check_in_time = now.strftime('%Y-%m-%d %H:%M:%S')

        # 5. Persist to database
        success = self.db.add_attendance(student_name, check_in_time, status, notes)
        if success:
            self._recent_logs[student_name] = now
            print(f'[ATTENDANCE] {student_name} -> {status} at {check_in_time}')

        return success

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _determine_status(self, dt: datetime.datetime) -> str:
        """
        Return 'Late' if current time is after the configured threshold,
        otherwise 'Present'.

        Future SaaS enhancement: make threshold configurable per campus
        or per attendance policy.
        """
        if dt.hour > self.LATE_HOUR:
            return 'Late'
        elif dt.hour == self.LATE_HOUR and dt.minute > self.LATE_MINUTE:
            return 'Late'
        return 'Present'

    def _auto_register_student(self, name: str) -> int:
        """
        Create a new student record when an unknown face is recognized.

        Generates a safe student_id from the name (e.g., 'Abhiraj Srivastava'
        becomes 'ABHIRAJ'). If that ID already exists, appends a numeric
        suffix until unique.

        Args:
            name (str): Full name of the newly detected student.

        Returns:
            int: The new student's database id.
        """
        # Generate a base ID from the name
        safe_id = re.sub(r'[^a-zA-Z0-9]', '', name).upper()[:6] or 'STU001'

        # Ensure uniqueness
        existing = self.db.get_all_students()
        existing_ids = {s['student_id'] for s in existing}
        original = safe_id
        counter = 1
        while safe_id in existing_ids:
            safe_id = f'{original[:3]}{counter:03d}'
            counter += 1

        # Generate a placeholder email
        email = f"{name.lower().replace(' ', '.')}@school.com"

        # Insert
        self.db.add_student(name, safe_id, email)
        print(f'[INFO] Auto-registered new student: {name} ({safe_id})')

        # Fetch and return the new id
        student = self.db.get_student_by_name(name)
        return student.get('id') if student else None

    def cleanup_old_logs(self, max_age_seconds: int = 60) -> None:
        """
        Remove stale entries from the in-memory throttle cache.
        Call this periodically to prevent memory growth.

        Args:
            max_age_seconds (int): Entries older than this are removed.
        """
        now = datetime.datetime.now()
        stale = [
            name for name, ts in self._recent_logs.items()
            if (now - ts).seconds > max_age_seconds
        ]
        for name in stale:
            del self._recent_logs[name]

