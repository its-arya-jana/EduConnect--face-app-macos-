import sqlite3
import os

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            department TEXT
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Present',
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Add timestamp column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE attendance ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        # Column already exists, ignore the error
        pass
    
    conn.commit()
    conn.close()

def add_student(name, roll_number, department):
    """Add a new student to the database"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO students (name, roll_number, department)
            VALUES (?, ?, ?)
        ''', (name, roll_number, department))
        
        conn.commit()
        student_id = cursor.lastrowid
        conn.close()
        return student_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def update_student(student_id, name, roll_number, department):
    """Update student information"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE students 
        SET name=?, roll_number=?, department=?
        WHERE id=?
    ''', (name, roll_number, department, student_id))
    
    conn.commit()
    conn.close()

def delete_student(student_id):
    """Delete a student from the database"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Delete attendance records first
    cursor.execute('DELETE FROM attendance WHERE student_id=?', (student_id,))
    
    # Delete student
    cursor.execute('DELETE FROM students WHERE id=?', (student_id,))
    
    conn.commit()
    conn.close()

def get_all_students():
    """Retrieve all students from the database"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    
    conn.close()
    return students

def get_student_by_id(student_id):
    """Retrieve a student by ID"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM students WHERE id=?', (student_id,))
    student = cursor.fetchone()
    
    conn.close()
    return student

def mark_attendance(student_id, date, time):
    """Mark attendance for a student"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Check if student already has attendance marked in the last 24 hours
    cursor.execute('''
        SELECT id FROM attendance 
        WHERE student_id = ? AND timestamp > datetime('now', '-1 day')
    ''', (student_id,))
    
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Student already marked in last 24 hours, don't mark again
        conn.close()
        return False
    
    # Insert new attendance record
    cursor.execute('''
        INSERT INTO attendance (student_id, date, time)
        VALUES (?, ?, ?)
    ''', (student_id, date, time))
    
    conn.commit()
    conn.close()
    return True

def get_attendance_report():
    """Get attendance report for all students"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.name, s.roll_number, a.date, a.time, a.status
        FROM students s
        JOIN attendance a ON s.id = a.student_id
        ORDER BY a.date, s.name
    ''')
    
    report = cursor.fetchall()
    conn.close()
    return report

def clear_old_attendance():
    """Clear attendance records older than 24 hours"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM attendance WHERE timestamp < datetime('now', '-1 day')")
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count

def get_todays_attendance_count(student_id):
    """Get count of attendance records for a student in the last 24 hours"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM attendance 
        WHERE student_id = ? AND timestamp > datetime('now', '-1 day')
    ''', (student_id,))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")