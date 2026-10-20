
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------------- CONFIGURATION ----------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "scholarship.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "pdf", "png", "jpg", "jpeg"
}


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CREATE DATABASE TABLES ----------------

def create_tables():
    conn = get_db_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                student_id TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                course TEXT NOT NULL,
                college TEXT NOT NULL,
                percentage TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                aadhaar TEXT,
                income_certificate TEXT,
                caste_certificate TEXT,
                marks_memo TEXT,
                bank_passbook TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                scholarship TEXT NOT NULL,
                academic_score TEXT NOT NULL,
                income TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
            )
        """)

        conn.commit()

    finally:
        conn.close()


# ---------------- HELPER FUNCTIONS ----------------

def get_student(student_id):
    conn = get_db_connection()

    try:
        return conn.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()
    finally:
        conn.close()


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ---------------- HOME ----------------

@app.route("/")
def home():
    conn = get_db_connection()

    try:
        student_count = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        application_count = conn.execute(
            "SELECT COUNT(*) FROM applications"
        ).fetchone()[0]

        scholarship_count = 4

    finally:
        conn.close()

    return render_template(
        "index.html",
        student_count=student_count,
        application_count=application_count,
        scholarship_count=scholarship_count
    )


# ---------------- SCHOLARSHIPS ----------------

@app.route("/scholarships")
def scholarships():
    return render_template("scholarships.html")


# ---------------- ELIGIBILITY ----------------

@app.route("/eligibility", methods=["GET", "POST"])
def eligibility():
    result = None

    if request.method == "POST":
        try:
            marks = float(request.form.get("marks", ""))
            income = float(
                request.form.get("familyIncome", "")
            )

            if not (0 <= marks <= 100) or income < 0:
                result = "Please enter valid marks and income."

            elif marks >= 60 and income <= 250000:
                result = (
                    "You meet the sample eligibility criteria. "
                    "Please verify official scheme rules."
                )

            else:
                result = (
                    "You do not meet these sample criteria. "
                    "Check the official scheme requirements."
                )

        except (ValueError, TypeError):
            result = "Please enter valid numeric details."

    return render_template(
        "eligibility.html",
        result=result
    )


# ---------------- STUDENT PROFILE ----------------

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        student_id = request.form.get("student_id", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        course = request.form.get("course", "").strip()
        college = request.form.get("college", "").strip()
        percentage = request.form.get("percentage", "").strip()

        if not all([
            name, student_id, email, phone,
            course, college, percentage
        ]):
            return (
                "Please complete all student profile fields.",
                400
            )

        try:
            score = float(percentage)

            if not 0 <= score <= 100:
                return "Percentage must be between 0 and 100.", 400

        except ValueError:
            return "Please enter a valid percentage.", 400

        conn = get_db_connection()

        try:
            conn.execute("""
                INSERT INTO students
                (
                    name, student_id, email, phone,
                    course, college, percentage
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name, student_id, email, phone,
                course, college, percentage
            ))

            conn.commit()

        except sqlite3.IntegrityError:
            return (
                "This Student ID already exists. "
                "Please use a different ID.",
                400
            )

        finally:
            conn.close()

        return redirect(url_for("student_profile"))

    conn = get_db_connection()

    try:
        student = conn.execute(
            "SELECT * FROM students ORDER BY id DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()

    return render_template(
        "profile.html",
        student_name=student["name"] if student else "No student registered",
        student_email=student["email"] if student else "Not available",
        college=student["college"] if student else "Not available",
        course=student["course"] if student else "Not available"
    )


# ---------------- DOCUMENT UPLOADS ----------------

@app.route("/documents", methods=["GET", "POST"])
def documents():

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()

        if not student_id or not get_student(student_id):
            return (
                "Please register the student profile first "
                "and enter a valid Student ID.",
                400
            )

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        field_names = [
            "aadhaar",
            "income_certificate",
            "caste_certificate",
            "marks_memo",
            "bank_passbook"
        ]

        saved_names = {}

        for field in field_names:
            uploaded_file = request.files.get(field)
            saved_names[field] = ""

            if uploaded_file and uploaded_file.filename:
                if not allowed_file(uploaded_file.filename):
                    return (
                        "Only PDF, PNG, JPG and JPEG files are allowed.",
                        400
                    )

                safe_name = secure_filename(
                    uploaded_file.filename
                )

                unique_name = (
                    uuid.uuid4().hex + "_" + safe_name
                )

                uploaded_file.save(
                    os.path.join(UPLOAD_FOLDER, unique_name)
                )

                saved_names[field] = unique_name

        conn = get_db_connection()

        try:
            conn.execute("""
                INSERT INTO documents
                (
                    student_id, aadhaar, income_certificate,
                    caste_certificate, marks_memo, bank_passbook
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                saved_names["aadhaar"],
                saved_names["income_certificate"],
                saved_names["caste_certificate"],
                saved_names["marks_memo"],
                saved_names["bank_passbook"]
            ))

            conn.commit()

        finally:
            conn.close()

        return (
            "Documents saved successfully. "
            "Please keep your Student ID for reference."
        )

    return render_template("documents.html")


# ---------------- SCHOLARSHIP APPLICATION ----------------

@app.route("/application", methods=["GET", "POST"])
def application():

    if request.method == "POST":
        student_id = request.form.get(
            "student_id", ""
        ).strip()

        scholarship = request.form.get(
            "scholarship", ""
        ).strip()

        academic_score = request.form.get(
            "academic_score", ""
        ).strip()

        income = request.form.get(
            "income", ""
        ).strip()

        category = request.form.get(
            "category", ""
        ).strip()

        if not all([
            student_id, scholarship,
            academic_score, income, category
        ]):
            return (
                "Please complete all application fields.",
                400
            )

        student = get_student(student_id)

        if not student:
            return (
                "Student ID not found. "
                "Please register your profile first.",
                400
            )

        try:
            score = float(academic_score)
            family_income = float(income)

            if not 0 <= score <= 100 or family_income < 0:
                return "Please enter valid marks and income.", 400

        except ValueError:
            return "Marks and income must be valid numbers.", 400

        conn = get_db_connection()

        try:
            cursor = conn.execute("""
                INSERT INTO applications
                (
                    student_id, scholarship,
                    academic_score, income, category, status
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                scholarship,
                academic_score,
                income,
                category,
                "Pending"
            ))

            conn.commit()
            application_id = cursor.lastrowid

        finally:
            conn.close()

        return redirect(
            url_for("status", application_id=application_id)
        )

    return render_template("application.html")


# ---------------- APPLICATION STATUS ----------------

@app.route("/status")
def status():
    application_id = request.args.get("application_id")

    conn = get_db_connection()

    try:
        if application_id:
            applications = conn.execute("""
                SELECT applications.*,
                       students.name AS student_name
                FROM applications
                LEFT JOIN students
                ON applications.student_id = students.student_id
                WHERE applications.id = ?
            """, (application_id,)).fetchall()
        else:
            applications = conn.execute("""
                SELECT applications.*,
                       students.name AS student_name
                FROM applications
                LEFT JOIN students
                ON applications.student_id = students.student_id
                ORDER BY applications.id DESC
            """).fetchall()

    finally:
        conn.close()

    latest_status = (
        applications[0]["status"]
        if applications
        else "No applications submitted yet"
    )

    return render_template(
        "status.html",
        applications=applications,
        application_status=latest_status
    )


# ---------------- STUDENT DETAILS ----------------

@app.route("/student-profile")
def student_profile():
    conn = get_db_connection()

    try:
        student = conn.execute("""
            SELECT * FROM students
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

        if student:
            latest_application = conn.execute("""
                SELECT * FROM applications
                WHERE student_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (student["student_id"],)).fetchone()
        else:
            latest_application = None

    finally:
        conn.close()

    return render_template(
        "student_profile.html",
        student_id=student["student_id"] if student else "N/A",
        student_name=student["name"] if student else "No student registered",
        student_email=student["email"] if student else "N/A",
        college=student["college"] if student else "N/A",
        course=student["course"] if student else "N/A",
        study_year="Not specified",
        scholarship_name=(
            latest_application["scholarship"]
            if latest_application else "No application"
        ),
        application_status=(
            latest_application["status"]
            if latest_application else "No application"
        )
    )


# ---------------- ERROR HANDLING ----------------

@app.errorhandler(413)
def file_too_large(error):
    return "File is too large. Maximum total request size is 10 MB.", 413


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
