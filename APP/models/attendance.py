"""
app/models/attendance.py
========================
AttendanceLog data model and schema definition.

This module defines the structure for daily attendance records.
Each row represents one student's attendance status for a specific date.

The database enforces a UNIQUE constraint on (student_id, date) so that
a student can only have one primary attendance record per day.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AttendanceLog:
    """
    Represents a single attendance record.

    Attributes:
        id (int): Auto-increment primary key.
        student_id (int): Foreign key referencing students.id.
        student_name (str): Denormalized name (populated on JOIN queries).
        check_in_time (datetime): When the student was first detected.
        check_out_time (datetime): Optional logout timestamp.
        date (str): Date string in YYYY-MM-DD format.
        status (str): 'Present', 'Absent', or 'Late'.
        notes (str): Optional detail (e.g., 'Face detected', 'Arrived after 10 AM').
    """
    id: int = 0
    student_id: int = 0
    student_name: Optional[str] = None  # populated from JOIN
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    date: str = ''
    status: str = 'Present'
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'AttendanceLog':
        """Build an AttendanceLog from a dictionary (e.g., DB row)."""
        return cls(
            id=data.get('id', 0),
            student_id=data.get('student_id', 0),
            student_name=data.get('student_name'),
            check_in_time=data.get('check_in_time'),
            check_out_time=data.get('check_out_time'),
            date=data.get('date', ''),
            status=data.get('status', 'Present'),
            notes=data.get('notes')
        )

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary for JSON responses."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'date': self.date,
            'status': self.status,
            'notes': self.notes
        }


# ------------------------------------------------------------------
# Schema definition
# ------------------------------------------------------------------

ATTENDANCE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS attendance_logs (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    check_in_time TIMESTAMP NOT NULL,
    check_out_time TIMESTAMP,
    date DATE NOT NULL,
    status TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE(student_id, date)
);
"""

