"""
app/database/db.py
==================
Database Manager for the Attendance Management System.

Supports PostgreSQL (via psycopg2) with automatic fallback to SQLite
for local development when PostgreSQL is unavailable.
"""

import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
load_dotenv(os.path.join(basedir, '.env'))

POSTGRES_AVAILABLE = False
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except Exception as e:
    print(f'[INFO] psycopg2 not available ({e}); using SQLite fallback.')


def _dict_factory(cursor, row):
    """SQLite row factory to mimic psycopg2 RealDictCursor."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DatabaseManager:
    def __init__(self):
        self.use_postgres = False
        self.sqlite_path = os.path.join(basedir, 'instance', 'attendance.db')
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)

        if POSTGRES_AVAILABLE:
            self.conn_params = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'dbname': os.getenv('DB_NAME', 'attendance_db'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', ''),
                'port': int(os.getenv('DB_PORT', '5432'))
            }
            try:
                self._test_postgres()
                self.use_postgres = True
                print('[INFO] Using PostgreSQL database.')
            except Exception as e:
                print(f'[WARN] PostgreSQL unavailable ({e}); falling back to SQLite.')
                self.use_postgres = False
        else:
            print('[INFO] Using SQLite database.')

        self.init_database()

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def _test_postgres(self):
        conn = psycopg2.connect(**self.conn_params)
        conn.cursor().execute('SELECT 1')
        conn.close()

    def get_connection(self):
        if self.use_postgres:
            return psycopg2.connect(**self.conn_params)
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = _dict_factory
        return conn

    def _cursor(self, conn):
        if self.use_postgres:
            return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return conn.cursor()

    def _execute(self, cursor, sql, params=()):
        """Normalize param style for SQLite vs PostgreSQL."""
        if self.use_postgres:
            return cursor.execute(sql, params)
        # SQLite uses ? instead of %s
        sql = sql.replace('%s', '?')
        return cursor.execute(sql, params)

    # ------------------------------------------------------------------
    # Schema initialization
    # ------------------------------------------------------------------

    def init_database(self):
        conn = self.get_connection()
        cursor = self._cursor(conn)

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY {},
                name TEXT NOT NULL UNIQUE,
                student_id TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''.format('AUTOINCREMENT' if not self.use_postgres else 'AUTO_INCREMENT'))

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY {},
                student_id INTEGER NOT NULL,
                check_in_time TIMESTAMP NOT NULL,
                check_out_time TIMESTAMP,
                date DATE NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id),
                UNIQUE(student_id, date)
            )
        '''.format('AUTOINCREMENT' if not self.use_postgres else 'AUTO_INCREMENT'))

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY {},
                date DATE NOT NULL UNIQUE,
                total_students INTEGER DEFAULT 0,
                present INTEGER DEFAULT 0,
                absent INTEGER DEFAULT 0,
                late INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''.format('AUTOINCREMENT' if not self.use_postgres else 'AUTO_INCREMENT'))

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_status (
                id INTEGER PRIMARY KEY {},
                device_name TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'Active',
                last_seen TIMESTAMP,
                uptime_seconds INTEGER DEFAULT 0,
                details TEXT
            )
        '''.format('AUTOINCREMENT' if not self.use_postgres else 'AUTO_INCREMENT'))

        conn.commit()
        conn.close()
        self._insert_sample_data()

    def _insert_sample_data(self):
        conn = self.get_connection()
        cursor = self._cursor(conn)

        cursor.execute('SELECT COUNT(*) FROM students')
        count_row = cursor.fetchone()
        count_val = count_row.get('COUNT(*)') if isinstance(count_row, dict) and 'COUNT(*)' in count_row else (count_row[0] if count_row else 0)
        if count_val == 0:
            sample_students = [
                ('Abhiraj Srivastava', 'STU001', 'abhiraj@school.com', '9876543210'),
                ('Rahul Sharma', 'STU002', 'rahul@school.com', '9876543211'),
                ('Sanya Malhotra', 'STU003', 'sanya@school.com', '9876543212'),
                ('Vikram Singh', 'STU004', 'vikram@school.com', '9876543213'),
                ('Anjali Rao', 'STU005', 'anjali@school.com', '9876543214'),
                ('Arya Panday', 'STU006', 'arya@school.com', '9876543215'),
            ]
            for name, sid, email, phone in sample_students:
                self._execute(cursor, '''
                    INSERT OR IGNORE INTO students (name, student_id, email, phone)
                    VALUES (%s, %s, %s, %s)
                ''', (name, sid, email, phone))
            conn.commit()

        cursor.execute('SELECT COUNT(*) FROM attendance_logs')
        count_row = cursor.fetchone()
        count_val = count_row.get('COUNT(*)') if isinstance(count_row, dict) and 'COUNT(*)' in count_row else (count_row[0] if count_row else 0)
        if count_val == 0:
            today = datetime.now().strftime('%Y-%m-%d')
            sample_logs = [
                (1, f'{today} 09:15:00', None, today, 'Present', 'Face detected'),
                (2, f'{today} 08:50:00', None, today, 'Present', 'Face detected'),
                (3, f'{today} 09:45:00', None, today, 'Present', 'Face detected'),
                (5, f'{today} 09:05:00', None, today, 'Present', 'Face detected'),
                (6, f'{today} 10:10:00', None, today, 'Late', 'Arrived after 10 AM'),
            ]
            for sid, check_in, check_out, date, status, notes in sample_logs:
                self._execute(cursor, '''
                    INSERT OR IGNORE INTO attendance_logs (student_id, check_in_time, check_out_time, date, status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (sid, check_in, check_out, date, status, notes))
            conn.commit()

        conn.close()

    # ------------------------------------------------------------------
    # Student operations
    # ------------------------------------------------------------------

    def get_all_students(self):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        cursor.execute('SELECT * FROM students ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_student(self, student_id):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        self._execute(cursor, 'SELECT * FROM students WHERE id = %s', (student_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}

    def get_student_by_name(self, name):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        self._execute(cursor, 'SELECT * FROM students WHERE name = %s', (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}

    def add_student(self, name, student_id, email, phone=None):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        try:
            self._execute(cursor, '''
                INSERT INTO students (name, student_id, email, phone)
                VALUES (%s, %s, %s, %s)
            ''', (name, student_id, email, phone))
            conn.commit()
            inserted = cursor.rowcount > 0
        except Exception:
            inserted = False
        conn.close()
        return inserted

    def update_student(self, student_id, **kwargs):
        allowed_fields = ['name', 'email', 'phone', 'status']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return

        conn = self.get_connection()
        cursor = self._cursor(conn)
        set_clause = ', '.join([f'{k} = %s' for k in updates.keys()])
        values = list(updates.values()) + [student_id]
        self._execute(cursor, f'UPDATE students SET {set_clause} WHERE id = %s', values)
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Attendance operations
    # ------------------------------------------------------------------

    def get_all_attendance_logs(self, limit=50):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        self._execute(cursor, '''
            SELECT al.*, s.name AS student_name, s.student_id AS student_id_num
            FROM attendance_logs al
            JOIN students s ON al.student_id = s.id
            ORDER BY al.check_in_time DESC
            LIMIT %s
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_attendance_by_date(self, date):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        self._execute(cursor, '''
            SELECT al.*, s.name AS student_name
            FROM attendance_logs al
            JOIN students s ON al.student_id = s.id
            WHERE al.date = %s
            ORDER BY al.check_in_time
        ''', (date,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_student_attendance(self, student_id, limit=30):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        self._execute(cursor, '''
            SELECT * FROM attendance_logs
            WHERE student_id = %s
            ORDER BY date DESC
            LIMIT %s
        ''', (student_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_attendance(self, student_name, check_in_time, status='Present', notes=''):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        self._execute(cursor, 'SELECT id FROM students WHERE name = %s', (student_name,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False

        student_id = result['id']
        date = check_in_time.split(' ')[0]
        try:
            self._execute(cursor, '''
                INSERT INTO attendance_logs (student_id, check_in_time, date, status, notes)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT(student_id, date) DO UPDATE SET
                    check_in_time = excluded.check_in_time,
                    status = excluded.status,
                    notes = excluded.notes
            ''', (student_id, check_in_time, date, status, notes))
            conn.commit()
            success = True
        except Exception as e:
            print(f'[WARN] Attendance insert failed: {e}')
            success = False
        conn.close()
        return success

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_daily_stats(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        conn = self.get_connection()
        cursor = self._cursor(conn)
        self._execute(cursor, '''
            SELECT COUNT(*) AS total,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent,
                SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) AS late
            FROM attendance_logs
            WHERE date = %s
        ''', (date,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}

    def get_weekly_stats(self, week_offset=0):
        from datetime import timedelta
        end_date = datetime.now() - timedelta(days=week_offset * 7)
        start_date = end_date - timedelta(days=6)
        conn = self.get_connection()
        cursor = self._cursor(conn)
        self._execute(cursor, '''
            SELECT date,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent,
                SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) AS late
            FROM attendance_logs
            WHERE date BETWEEN %s AND %s
            GROUP BY date
            ORDER BY date
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def _extract_count(row):
        """Extract COUNT(*) value from both PostgreSQL and SQLite rows."""
        if row is None:
            return 0
        if isinstance(row, dict):
            for key in row:
                if 'count' in key.lower():
                    return row[key] or 0
            return 0
        return row[0] or 0

    def get_attendance_stats(self):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = self._extract_count(cursor.fetchone())

        today = datetime.now().strftime('%Y-%m-%d')
        self._execute(cursor,
            "SELECT COUNT(*) FROM attendance_logs WHERE date = %s AND status = 'Present'",
            (today,))
        present = self._extract_count(cursor.fetchone())
        self._execute(cursor,
            "SELECT COUNT(*) FROM attendance_logs WHERE date = %s AND status = 'Absent'",
            (today,))
        absent = self._extract_count(cursor.fetchone())
        self._execute(cursor,
            "SELECT COUNT(*) FROM attendance_logs WHERE date = %s AND status = 'Late'",
            (today,))
        late = self._extract_count(cursor.fetchone())
        self._execute(cursor, '''
            SELECT COUNT(DISTINCT student_id)
            FROM attendance_logs
            WHERE date = %s AND status IN ('Present', 'Late')
        ''', (today,))
        unique_present = self._extract_count(cursor.fetchone())
        conn.close()

        return {
            'total_students': total_students,
            'present_today': unique_present,
            'absent_today': total_students - unique_present,
            'late_today': late,
            'attendance_rate': round((unique_present / total_students * 100), 1)
            if total_students > 0 else 0
        }

    # ------------------------------------------------------------------
    # Device status
    # ------------------------------------------------------------------

    def update_device_status(self, device_name, status, details=None):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        try:
            self._execute(cursor, '''
                INSERT INTO device_status (device_name, status, last_seen, details)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT(device_name) DO UPDATE SET
                    status = excluded.status,
                    last_seen = excluded.last_seen,
                    details = excluded.details
            ''', (device_name, status, datetime.now(), details))
            conn.commit()
        except Exception as e:
            # SQLite < 3.24 doesn't support UPSERT; fallback to manual replace
            self._execute(cursor, 'DELETE FROM device_status WHERE device_name = %s', (device_name,))
            self._execute(cursor, '''
                INSERT INTO device_status (device_name, status, last_seen, details)
                VALUES (%s, %s, %s, %s)
            ''', (device_name, status, datetime.now(), details))
            conn.commit()
        conn.close()

    def get_device_status(self, device_name=None):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        if device_name:
            self._execute(cursor, 'SELECT * FROM device_status WHERE device_name = %s', (device_name,))
            row = cursor.fetchone()
            device = dict(row) if row else {}
        else:
            cursor.execute('SELECT * FROM device_status')
            rows = cursor.fetchall()
            device = [dict(row) for row in rows]
        conn.close()
        return device

    def get_unique_faces_count(self):
        conn = self.get_connection()
        cursor = self._cursor(conn)
        cursor.execute('SELECT COUNT(DISTINCT student_id) FROM attendance_logs')
        count = self._extract_count(cursor.fetchone())
        conn.close()
        return count

