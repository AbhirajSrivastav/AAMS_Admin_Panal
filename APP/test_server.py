import os
from flask import Flask, jsonify
from database import DatabaseManager

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)), static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))

db = DatabaseManager()

@app.route('/api/stats')
def get_stats():
    stats = db.get_attendance_stats()
    return jsonify(stats)

@app.route('/api/students')
def get_students():
    students = db.get_all_students()
    return jsonify(students)

@app.route('/api/device-status')
def get_device_status():
    devices = db.get_device_status()
    return jsonify(devices)

if __name__ == '__main__':
    print("Starting Flask test server on port 5000...")
    app.run(debug=True, use_reloader=False)

