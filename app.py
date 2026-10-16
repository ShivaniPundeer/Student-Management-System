
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect_db()
    columns = conn.execute("PRAGMA table_info(students)").fetchall()

    if columns:
        names = [column["name"] for column in columns]
        if not {"id", "name", "roll", "course", "marks"}.issubset(names):
            conn.execute("ALTER TABLE students RENAME TO students_legacy")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            course TEXT NOT NULL,
            marks INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


@app.route("/api/students", methods=["GET"])
def get_students():
    conn = connect_db()
    rows = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    roll = str(data.get("roll", "")).strip()
    course = str(data.get("course", "")).strip()

    try:
        marks = int(data.get("marks"))
    except (TypeError, ValueError):
        return jsonify({"error": "Marks must be a number"}), 400

    if not name or not roll or not course:
        return jsonify({"error": "All fields are required"}), 400

    if not 0 <= marks <= 100:
        return jsonify({"error": "Marks must be between 0 and 100"}), 400

    conn = connect_db()
    cursor = conn.execute(
        "INSERT INTO students (name, roll, course, marks) VALUES (?, ?, ?, ?)",
        (name, roll, course, marks)
    )
    conn.commit()
    student_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Student added successfully!",
        "id": student_id,
        "name": name,
        "roll": roll,
        "course": course,
        "marks": marks
    }), 201


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = connect_db()
    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?", (student_id,)
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully!"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)

