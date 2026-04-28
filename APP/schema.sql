-- AAMS PostgreSQL Database Schema
-- Run this file to initialize your PostgreSQL database manually
-- Or let database.py auto-create tables on first run

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    student_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    status TEXT DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_students INTEGER DEFAULT 0,
    present INTEGER DEFAULT 0,
    absent INTEGER DEFAULT 0,
    late INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS device_status (
    id SERIAL PRIMARY KEY,
    device_name TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'Active',
    last_seen TIMESTAMP,
    uptime_seconds INTEGER DEFAULT 0,
    details TEXT
);

-- Insert sample students (optional)
INSERT INTO students (name, student_id, email, phone) VALUES
('Abhiraj Srivastava', 'STU001', 'abhiraj@school.com', '9876543210'),
('Rahul Sharma', 'STU002', 'rahul@school.com', '9876543211'),
('Sanya Malhotra', 'STU003', 'sanya@school.com', '9876543212'),
('Vikram Singh', 'STU004', 'vikram@school.com', '9876543213'),
('Anjali Rao', 'STU005', 'anjali@school.com', '9876543214'),
('Arya Panday', 'STU006', 'arya@school.com', '9876543215')
ON CONFLICT DO NOTHING;
