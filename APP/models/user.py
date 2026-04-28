"""
app/models/user.py
==================
User data model for administrators and system operators.

This model is provided as a scaffold for future authentication features.
Currently, the system operates in single-admin mode, but adding
multi-user support (e.g., teachers, campus managers) is a common
SaaS requirement.

Planned fields:
    - id, username, email, password_hash, role, is_active, created_at

Future integration:
    - Flask-Login for session management
    - Flask-Bcrypt for password hashing
    - Role-based access control (RBAC)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    Represents an administrative user of the system.

    Attributes:
        id (int): Auto-increment primary key.
        username (str): Unique login handle.
        email (str): Unique email address.
        password_hash (str): Hashed password (never store plain text).
        role (str): 'admin', 'teacher', 'viewer', etc.
        is_active (bool): Whether the account is enabled.
        created_at (datetime): Account creation timestamp.
    """
    id: int = 0
    username: str = ''
    email: str = ''
    password_hash: str = ''
    role: str = 'viewer'
    is_active: bool = True
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Build a User from a dictionary."""
        return cls(
            id=data.get('id', 0),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            role=data.get('role', 'viewer'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at')
        )

    def to_dict(self) -> dict:
        """Serialize to dictionary (excludes password_hash for safety)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------
# Schema definition (create when auth is implemented)
# ------------------------------------------------------------------

USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

