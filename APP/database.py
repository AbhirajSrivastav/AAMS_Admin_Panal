import psycopg2
import psycopg2.extras
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'dbname': os.getenv('DB_NAME', 'attendance_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', '5432'))
        }
        self.init_database()

    def get_connection(self):
        try:
            conn = psycopg2.connect(**self.conn_params)
            return conn
        except psycopg2.OperationalError as e:
            print(f'[ERROR] Could not connect to PostgreSQL: {e}')
            print('[INFO] Please check your .env file and ensure PostgreSQL is running.')
            raise

    def _ensure_connection(self, max_retries=3):
        for attempt in range(1, max_retries + 1):
            try:
                conn = self.get_connection()
                conn.cursor().execute('SELECT 1')
                conn.close()
                return True
            except Exception as e:
                print(f'[WARN] DB connection attempt {attempt}/{max_retries} failed: {e}')
        raise ConnectionError('Failed to connect to PostgreSQL after retries.')

    def init_database(self):
        self._ensure_connection()
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            student_id TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS attendance_logs (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL,
            check_in_time TIMESTAMP NOT NULL,
            check_out_time TIMESTAMP,
            date DATE NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id),
            UNIQUE(student_id, date)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS daily_stats (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL UNIQUE,
            total_students INTEGER DEFAULT 0,
            present INTEGER DEFAULT 0,
            absent INTEGER DEFAULT 0,
            late INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS device_status (
            id SERIAL PRIMARY KEY,
            device_name TEXT NOT NULL UNIQUE,
            status TEXT DEFAULT 'Active',
            last_seen TIMESTAMP,
            uptime_seconds INTEGER DEFAULT 0,
            details TEXT
        )''')

        conn.commit()
        conn.close()
        self._insert_sample_data()

    def _insert_sample_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM students')
        if cursor.fetchone()[0] == 0:
            sample_students = [
                ('Abhiraj Srivastava', 'STU001', 'abhiraj@school.com', '9876543210'),
                ('Rahul Sharma', 'STU002', 'rahul@school.com', '9876543211'),
                ('Sanya Malhotra', 'STU003', 'sanya@school.com', '9876543212'),
                ('Vikram Singh', 'STU004', 'vikram@school.com', '9876543213'),
                ('Anjali Rao', 'STU005', 'anjali@school.com', '9876543214'),
                ('Arya Panday', 'STU006', 'arya@school.com', '9876543215'),
            ]
            for name, sid, email, phone in sample_students:
                cursor.execute('''INSERT INTO students (name, student_id, email, phone)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING''', (name, sid, email, phone))
            conn.commit()

        cursor.execute('SELECT COUNT(*) FROM attendance_logs')
        if cursor.fetchone()[0] == 0:
            today = datetime.now().strftime('%Y-%m-%d')
            sample_logs = [
                (1, f'{today} 09:15:00', None, today, 'Present', 'Face detected'),
                (2, f'{today} 08:50:00', None, today, 'Present', 'Face detected'),
                (3, f'{today} 09:45:00', None, today, 'Present', 'Face detected'),
                (5, f'{today} 09:05:00', None, today, 'Present', 'Face detected'),
                (6, f'{today} 10:10:00', None, today, 'Late', 'Arrived after 10 AM'),
            ]
            for sid, check_in, check_out, date, status, notes in sample_logs:
                cursor.execute('''INSERT INTO attendance_logs (student_id, check_in_time, check_out_time, date, status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING''', (sid, check_in, check_out, date, status, notes))
            conn.commit()

        conn.close()

    def get_all_students(self):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM students ORDER BY name')
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return students

    def get_student(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
        student = dict(cursor.fetchone() or {})
        conn.close()
        return student

    def add_student(self, name, student_id, email, phone=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO students (name, student_id, email, phone)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING''', (name, student_id, email, phone))
        conn.commit()
        inserted = cursor.rowcount > 0
        conn.close()
        return inserted

    def update_student(self, student_id, **kwargs):
        conn = self.get_connection()
        cursor = conn.cursor()
        allowed_fields = ['name', 'email', 'phone', 'status']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if updates:
            set_clause = ', '.join([f'{k} = %s' for k in updates.keys()])
            values = list(updates.values()) + [student_id]
            cursor.execute(f'UPDATE students SET {set_clause} WHERE id = %s', values)
            conn.commit()
        conn.close()

    def get_all_attendance_logs(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('''SELECT al.*, s.name AS student_name, s.student_id AS student_id_num
            FROM attendance_logs al
            JOIN students s ON al.student_id = s.id
            ORDER BY al.check_in_time DESC LIMIT %s''', (limit,))
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    def get_attendance_by_date(self, date):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('''SELECT al.*, s.name AS student_name
            FROM attendance_logs al
            JOIN students s ON al.student_id = s.id
            WHERE al.date = %s ORDER BY al.check_in_time''', (date,))
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    def get_student_attendance(self, student_id, limit=30):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('''SELECT * FROM attendance_logs
            WHERE student_id = %s ORDER BY date DESC LIMIT %s''', (student_id, limit))
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    def add_attendance(self, student_name, check_in_time, status='Present', notes=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM students WHERE name = %s', (student_name,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False
        student_id = result[0]
        date = check_in_time.split(' ')[0]
        cursor.execute('''INSERT INTO attendance_logs (student_id, check_in_time, date, status, notes)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (student_id, date) DO UPDATE SET
                check_in_time = EXCLUDED.check_in_time,
                status = EXCLUDED.status,
                notes = EXCLUDED.notes''', (student_id, check_in_time, date, status, notes))
        conn.commit()
        conn.close()
        return True

    def get_daily_stats(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('''SELECT COUNT(*) AS total,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent,
            SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) AS late
            FROM attendance_logs WHERE date = %s''', (date,))
        result = dict(cursor.fetchone() or {})
        conn.close()
        return result

    def get_weekly_stats(self, week_offset=0):
        from datetime import datetime, timedelta
        end_date = datetime.now() - timedelta(days=week_offset*7)
        start_date = end_date - timedelta(days=6)
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute('''SELECT date,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent,
            SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) AS late
            FROM attendance_logs
            WHERE date BETWEEN %s AND %s
            GROUP BY date ORDER BY date''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        stats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return stats

    def get_attendance_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM attendance_logs WHERE date = %s AND status = 'Present'", (today,))
        present = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM attendance_logs WHERE date = %s AND status = 'Absent'", (today,))
        absent = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM attendance_logs WHERE date = %s AND status = 'Late'", (today,))
        late = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT student_id) FROM attendance_logs WHERE date = %s AND status IN ('Present', 'Late')", (today,))
        unique_present = cursor.fetchone()[0]
        conn.close()
        return {
            'total_students': total_students,
            'present_today': unique_present,
            'absent_today': total_students - unique_present,
            'late_today': late,
            'attendance_rate': round((unique_present / total_students * 100), 1) if total_students > 0 else 0
        }

    def update_device_status(self, device_name, status, details=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO device_status (device_name, status, last_seen, details)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (device_name) DO UPDATE SET
                status = EXCLUDED.status,
                last_seen = EXCLUDED.last_seen,
                details = EXCLUDED.details''', (device_name, status, datetime.now(), details))
        conn.commit()
        conn.close()

    def get_device_status(self, device_name=None):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if device_name:
            cursor.execute('SELECT * FROM device_status WHERE device_name = %s', (device_name,))
            device = dict(cursor.fetchone() or {})
        else:
            cursor.execute('SELECT * FROM device_status')
            device = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return device

    def get_unique_faces_count(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(DISTINCT student_id) FROM attendance_logs')
        count = cursor.fetchone()[0]
        conn.close()
        return count

