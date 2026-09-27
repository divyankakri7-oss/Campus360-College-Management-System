from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "campus360-secret-key-2026"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


# ============================================================
# PASSWORD HELPERS
# ============================================================

def is_password_hashed(password):

    if not password:
        return False

    return (
        password.startswith("scrypt:")
        or password.startswith("pbkdf2:")
    )


def secure_password(password):

    if is_password_hashed(password):
        return password

    return generate_password_hash(password)


# ============================================================
# MIGRATE OLD PLAIN-TEXT PASSWORDS
# ============================================================

def migrate_passwords():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, password
        FROM users
    """)

    users = cursor.fetchall()

    update_cursor = db.cursor()

    for user in users:

        old_password = user["password"]

        if not is_password_hashed(old_password):

            new_password = generate_password_hash(
                old_password
            )

            update_cursor.execute("""
                UPDATE users
                SET password=%s
                WHERE id=%s
            """, (
                new_password,
                user["id"]
            ))

    db.commit()

    update_cursor.close()
    cursor.close()
    db.close()


# ============================================================
# ROLE SECURITY
# ============================================================

def role_required(*allowed_roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:

                return redirect(
                    url_for("home")
                )

            if session.get("role") not in allowed_roles:

                return "Access Denied", 403

            return func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================
# LOGIN
# ============================================================

@app.route("/", methods=["GET", "POST"])
def home():

    message = ""

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]
        role = request.form["role"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM users
            WHERE email=%s
            AND role=%s
        """, (
            email,
            role
        ))

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            if user["role"] == "Admin":

                return redirect(
                    url_for("admin_dashboard")
                )

            elif user["role"] == "Faculty":

                return redirect(
                    url_for("faculty_dashboard")
                )

            else:

                return redirect(
                    url_for("dashboard")
                )

        message = "Invalid email, password or user type!"

    return render_template(
        "login.html",
        message=message
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@app.route("/dashboard")
@role_required("Student")
def dashboard():

    return render_template(
        "dashboard.html"
    )


# ============================================================
# STUDENT PROFILE
# ============================================================

@app.route("/profile")
@role_required("Student")
def profile():

    return render_template(
        "profile.html"
    )


# ============================================================
# STUDENT ATTENDANCE
# ============================================================

@app.route("/attendance")
@role_required("Student")
def attendance():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM attendance
        WHERE student_email=%s
    """, (
        session["email"],
    ))

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "attendance.html",
        records=records
    )


# ============================================================
# STUDENT SUBJECTS
# ============================================================

@app.route("/subjects")
@role_required("Student")
def subjects():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM subjects
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "subjects.html",
        records=records
    )


# ============================================================
# STUDENT ASSIGNMENTS
# ============================================================

@app.route("/assignments")
@role_required("Student")
def assignments():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM assignments
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "assignments.html",
        records=records
    )


# ============================================================
# STUDENT NOTICES
# ============================================================

@app.route("/notices")
@role_required("Student")
def notices():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM notices
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "notices.html",
        records=records
    )


# ============================================================
# STUDENT TIMETABLE
# ============================================================

@app.route("/timetable")
@role_required("Student")
def timetable():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM timetable
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "timetable.html",
        records=records
    )


# ============================================================
# STUDENT COMPLAINTS
# ============================================================

@app.route(
    "/complaints",
    methods=["GET", "POST"]
)
@role_required("Student")
def complaints():

    message = ""

    if request.method == "POST":

        subject = request.form["subject"]
        description = request.form["description"]

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO complaints
            (
                student_email,
                subject,
                description
            )
            VALUES (%s, %s, %s)
        """, (
            session["email"],
            subject,
            description
        ))

        db.commit()

        cursor.close()
        db.close()

        message = "Complaint submitted successfully!"

    return render_template(
        "complaints.html",
        message=message
    )


# ============================================================
# STUDENT RESULT
# ============================================================

@app.route("/result")
@role_required("Student")
def result():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM results
        WHERE student_email=%s
        ORDER BY id
    """, (
        session["email"],
    ))

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "result.html",
        records=records
    )


# ============================================================
# STUDENT OLD REPORT
# ============================================================

@app.route("/reports")
@role_required("Student")
def reports():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM reports
        WHERE student_email=%s
        ORDER BY id DESC
    """, (
        session["email"],
    ))

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "reports.html",
        records=records
    )


# ============================================================
# FACULTY DASHBOARD
# ============================================================

@app.route("/faculty_dashboard")
@role_required("Faculty")
def faculty_dashboard():

    return render_template(
        "faculty_dashboard.html"
    )


# ============================================================
# FACULTY PROFILE
# ============================================================

@app.route("/faculty_profile")
@role_required("Faculty")
def faculty_profile():

    return render_template(
        "faculty_profile.html"
    )


# ============================================================
# FACULTY STUDENTS
# ============================================================

@app.route("/faculty_students")
@role_required("Faculty")
def faculty_students():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            role
        FROM users
        WHERE role='Student'
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "faculty_students.html",
        records=records
    )


# ============================================================
# FACULTY SINGLE STUDENT
# ============================================================

@app.route(
    "/faculty_student/<int:student_id>"
)
@role_required("Faculty")
def faculty_student(student_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            role
        FROM users
        WHERE id=%s
        AND role='Student'
    """, (
        student_id,
    ))

    student = cursor.fetchone()

    cursor.close()
    db.close()

    if not student:

        return "Student not found", 404

    return render_template(
        "faculty_student_profile.html",
        student=student
    )


# ============================================================
# FACULTY ATTENDANCE
# ============================================================

@app.route("/faculty_attendance")
@role_required("Faculty")
def faculty_attendance():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            users.id,
            users.name AS student_name,

            COALESCE(
                SUM(attendance.total_classes),
                0
            ) AS total_classes,

            COALESCE(
                SUM(attendance.attended_classes),
                0
            ) AS attended_classes

        FROM users

        LEFT JOIN attendance
        ON users.email =
           attendance.student_email

        WHERE users.role='Student'

        GROUP BY
            users.id,
            users.name

        ORDER BY users.name
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "faculty_attendance.html",
        records=records
    )


# ============================================================
# FACULTY ASSIGNMENTS
# ============================================================

@app.route("/faculty_assignments")
@role_required("Faculty")
def faculty_assignments():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM assignments
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "faculty_assignments.html",
        records=records
    )


# ============================================================
# FACULTY ASSIGNMENT DETAILS
# ============================================================

@app.route(
    "/faculty_assignment/<int:assignment_id>"
)
@role_required("Faculty")
def faculty_assignment(assignment_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM assignments
        WHERE id=%s
    """, (
        assignment_id,
    ))

    assignment = cursor.fetchone()

    if not assignment:

        cursor.close()
        db.close()

        return "Assignment not found", 404

    cursor.execute("""
        SELECT
            users.id,
            users.name,
            users.email,

            COALESCE(
                assignment_submissions.status,
                'Not Submitted'
            ) AS status,

            assignment_submissions.submitted_date

        FROM users

        LEFT JOIN assignment_submissions

        ON users.email =
           assignment_submissions.student_email

        AND assignment_submissions.assignment_id=%s

        WHERE users.role='Student'

        ORDER BY users.name

    """, (
        assignment_id,
    ))

    students = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "faculty_assignment_detail.html",
        assignment=assignment,
        students=students
    )


# ============================================================
# FACULTY NOTICES
# ============================================================

@app.route("/faculty_notices")
@role_required("Faculty")
def faculty_notices():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM notices
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "faculty_notices.html",
        records=records
    )


# ============================================================
# FACULTY TIMETABLE
# ============================================================

@app.route("/faculty_timetable")
@role_required("Faculty")
def faculty_timetable():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM timetable
        ORDER BY id
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "faculty_timetable.html",
        records=records
    )


# ============================================================
# FACULTY REPORTS
# ============================================================

@app.route("/faculty_reports")
@role_required("Faculty")
def faculty_reports():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM reports
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "faculty_reports.html",
        records=records
    )


# ============================================================
# FACULTY COMPLAINTS
# ============================================================

@app.route("/faculty_complaints")
@role_required("Faculty")
def faculty_complaints():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM complaints
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "faculty_complaints.html",
        records=records
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin_dashboard")
@role_required("Admin")
def admin_dashboard():

    return render_template(
        "admin_dashboard.html"
    )


# ============================================================
# ADMIN - STUDENT MANAGEMENT
# ============================================================

@app.route(
    "/admin_students",
    methods=["GET", "POST"]
)
@role_required("Admin")
def admin_students():

    message = ""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"].strip()
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id
            FROM users
            WHERE email=%s
        """, (
            email,
        ))

        existing_user = cursor.fetchone()

        if existing_user:

            message = "Email already registered!"

        else:

            cursor2 = db.cursor()

            cursor2.execute("""
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    'Student'
                )
            """, (
                name,
                email,
                generate_password_hash(
                    password
                )
            ))

            db.commit()

            cursor2.close()

            message = "Student added successfully!"

        cursor.close()
        db.close()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            role
        FROM users
        WHERE role='Student'
        ORDER BY id DESC
    """)

    students = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admin_students.html",
        students=students,
        message=message
    )


# ============================================================
# ADMIN - EDIT STUDENT
# ============================================================

@app.route(
    "/admin_student_edit/<int:student_id>",
    methods=["GET", "POST"]
)
@role_required("Admin")
def admin_student_edit(student_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            password
        FROM users
        WHERE id=%s
        AND role='Student'
    """, (
        student_id,
    ))

    student = cursor.fetchone()

    cursor.close()

    if not student:

        db.close()

        return "Student not found", 404

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"].strip()
        password = request.form["password"]

        password_to_save = secure_password(
            password
        )

        update_cursor = db.cursor()

        update_cursor.execute("""
            UPDATE users
            SET
                name=%s,
                email=%s,
                password=%s
            WHERE id=%s
            AND role='Student'
        """, (
            name,
            email,
            password_to_save,
            student_id
        ))

        db.commit()

        update_cursor.close()
        db.close()

        return redirect(
            url_for("admin_students")
        )

    db.close()

    return render_template(
        "admin_edit_student.html",
        student=student
    )


# ============================================================
# ADMIN - DELETE STUDENT
# ============================================================

@app.route(
    "/admin_student_delete/<int:student_id>",
    methods=["POST"]
)
@role_required("Admin")
def admin_student_delete(student_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT email
        FROM users
        WHERE id=%s
        AND role='Student'
    """, (
        student_id,
    ))

    student = cursor.fetchone()

    cursor.close()

    if not student:

        db.close()

        return "Student not found", 404

    email = student["email"]

    delete_cursor = db.cursor()

    delete_cursor.execute("""
        DELETE FROM attendance
        WHERE student_email=%s
    """, (
        email,
    ))

    delete_cursor.execute("""
        DELETE FROM assignment_submissions
        WHERE student_email=%s
    """, (
        email,
    ))

    delete_cursor.execute("""
        DELETE FROM results
        WHERE student_email=%s
    """, (
        email,
    ))

    delete_cursor.execute("""
        DELETE FROM complaints
        WHERE student_email=%s
    """, (
        email,
    ))

    delete_cursor.execute("""
        DELETE FROM reports
        WHERE student_email=%s
    """, (
        email,
    ))

    delete_cursor.execute("""
        DELETE FROM users
        WHERE id=%s
        AND role='Student'
    """, (
        student_id,
    ))

    db.commit()

    delete_cursor.close()
    db.close()

    return redirect(
        url_for("admin_students")
    )


# ============================================================
# ADMIN - FACULTY MANAGEMENT
# ============================================================

@app.route(
    "/admin_faculty",
    methods=["GET", "POST"]
)
@role_required("Admin")
def admin_faculty():

    message = ""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"].strip()
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id
            FROM users
            WHERE email=%s
        """, (
            email,
        ))

        existing_user = cursor.fetchone()

        if existing_user:

            message = "Email already registered!"

        else:

            cursor2 = db.cursor()

            cursor2.execute("""
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    'Faculty'
                )
            """, (
                name,
                email,
                generate_password_hash(
                    password
                )
            ))

            db.commit()

            cursor2.close()

            message = "Faculty added successfully!"

        cursor.close()
        db.close()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            role
        FROM users
        WHERE role='Faculty'
        ORDER BY id DESC
    """)

    faculty = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admin_faculty.html",
        faculty=faculty,
        message=message
    )


# ============================================================
# ADMIN - EDIT FACULTY
# ============================================================

@app.route(
    "/admin_faculty_edit/<int:faculty_id>",
    methods=["GET", "POST"]
)
@role_required("Admin")
def admin_faculty_edit(faculty_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            password
        FROM users
        WHERE id=%s
        AND role='Faculty'
    """, (
        faculty_id,
    ))

    faculty = cursor.fetchone()

    cursor.close()

    if not faculty:

        db.close()

        return "Faculty not found", 404

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"].strip()
        password = request.form["password"]

        password_to_save = secure_password(
            password
        )

        update_cursor = db.cursor()

        update_cursor.execute("""
            UPDATE users
            SET
                name=%s,
                email=%s,
                password=%s
            WHERE id=%s
            AND role='Faculty'
        """, (
            name,
            email,
            password_to_save,
            faculty_id
        ))

        db.commit()

        update_cursor.close()
        db.close()

        return redirect(
            url_for("admin_faculty")
        )

    db.close()

    return render_template(
        "admin_edit_faculty.html",
        faculty=faculty
    )


# ============================================================
# ADMIN - DELETE FACULTY
# ============================================================

@app.route(
    "/admin_faculty_delete/<int:faculty_id>",
    methods=["POST"]
)
@role_required("Admin")
def admin_faculty_delete(faculty_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM users
        WHERE id=%s
        AND role='Faculty'
    """, (
        faculty_id,
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(
        url_for("admin_faculty")
    )


# ============================================================
# ADMIN - REPORTS
# ============================================================

@app.route("/admin_reports")
@role_required("Admin")
def admin_reports():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Total students
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM users
        WHERE role='Student'
    """)

    total_students = cursor.fetchone()["total"]

    # Total faculty
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM users
        WHERE role='Faculty'
    """)

    total_faculty = cursor.fetchone()["total"]

    # Total assignments
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM assignments
    """)

    total_assignments = cursor.fetchone()["total"]

    # Total attendance records
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM attendance
    """)

    total_attendance = cursor.fetchone()["total"]

    # Submitted assignments
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM assignment_submissions
        WHERE status='Submitted'
    """)

    submitted_assignments = cursor.fetchone()["total"]

    # Not submitted assignments
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM assignment_submissions
        WHERE status='Not Submitted'
    """)

    not_submitted_assignments = cursor.fetchone()["total"]

    # Results
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM results
    """)

    total_results = cursor.fetchone()["total"]

    # Complaints
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM complaints
    """)

    total_complaints = cursor.fetchone()["total"]

    # Attendance summary
    cursor.execute("""
        SELECT
            COALESCE(
                SUM(total_classes),
                0
            ) AS total_classes,

            COALESCE(
                SUM(attended_classes),
                0
            ) AS attended_classes

        FROM attendance
    """)

    attendance_summary = cursor.fetchone()

    cursor.close()
    db.close()

    total_classes = (
        attendance_summary["total_classes"]
    )

    attended_classes = (
        attendance_summary["attended_classes"]
    )

    if total_classes > 0:

        attendance_percentage = round(
            (
                attended_classes /
                total_classes
            ) * 100,
            2
        )

    else:

        attendance_percentage = 0

    return render_template(
        "admin_reports.html",
        total_students=total_students,
        total_faculty=total_faculty,
        total_assignments=total_assignments,
        total_attendance=total_attendance,
        submitted_assignments=submitted_assignments,
        not_submitted_assignments=not_submitted_assignments,
        total_results=total_results,
        total_complaints=total_complaints,
        total_classes=total_classes,
        attended_classes=attended_classes,
        attendance_percentage=attendance_percentage
    )


# ============================================================
# ADMIN - USER MANAGEMENT
# ============================================================

@app.route("/admin_users")
@role_required("Admin")
def admin_users():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            role
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admin_users.html",
        users=users
    )


# ============================================================
# ADMIN - CHANGE ROLE
# ============================================================

@app.route(
    "/admin_user_role/<int:user_id>",
    methods=["POST"]
)
@role_required("Admin")
def admin_user_role(user_id):

    new_role = request.form["role"]

    allowed_roles = [
        "Student",
        "Faculty",
        "Admin"
    ]

    if new_role not in allowed_roles:

        return "Invalid role", 400

    if user_id == session.get("user_id"):

        return (
            "You cannot change your own active role.",
            400
        )

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE users
        SET role=%s
        WHERE id=%s
    """, (
        new_role,
        user_id
    ))

    db.commit()

    cursor.close()
    db.close()

    return redirect(
        url_for("admin_users")
    )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    # Convert old plain-text passwords to hashes
    migrate_passwords()

    app.run(debug=True)