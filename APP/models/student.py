"""
app/models/student.py
=====================
Student data model and schema definition.

In a raw-SQL architecture, this module serves as:
    1. A type-safe dataclass for student records.
    2. A single source of truth for the students table schema.
    3. A factory for creating Student objects from dicts (e.g., DB rows).

Future SaaS migration:
    Replace this dataclass with a SQLAlchemy ORM model to gain
    automatic query building, relationships, and migrations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Student:
    """
    Represents a student in the attendance system.

    Attributes:
        id (int): Auto-increment primary key.
        name (str): Full name of the student (unique).
        student_id (str): External identifier, e.g., 'STU001' (unique).
        email (str): Contact email address (unique).
        phone (str): Optional phone number.
        status (str): 'Active' or 'Inactive'.
        created_at (datetime): Timestamp of record creation.
    """
    id: int = 0
    name: str = ''
    student_id: str = ''
    email: str = ''
    phone: Optional[str] = None
    status: str = 'Active'
    created_at: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Class methods
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        """
        Construct a Student instance from a dictionary (e.g., a DB row).

        Args:
            data (dict): Dictionary with keys matching Student fields.

        Returns:
            Student: Populated dataclass instance.
        """
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            student_id=data.get('student_id', ''),
            email=data.get('email', ''),
            phone=data.get('phone'),
            status=data.get('status', 'Active'),
            created_at=data.get('created_at')
        )

    # ------------------------------------------------------------------
    # Instance helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the Student back to a plain dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'student_id': self.student_id,
            'email': self.email,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------
# Schema definition (single source of truth for table structure)
# ------------------------------------------------------------------

STUDENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    student_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

