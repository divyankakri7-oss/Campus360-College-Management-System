# Campus360 – College Management System

Campus360 is a web-based College Management System designed to manage
student, faculty, and administrative activities from a single platform.

## Project Overview

The system provides role-based access for:

- Student
- Faculty
- Admin

Each role gets a separate dashboard and features according to its responsibilities.

## Main Features

### Student Module

- Student Login
- Student Dashboard
- Profile
- Attendance
- Subjects
- Assignments
- Notices
- Timetable
- Academic Result
- Complaints

### Faculty Module

- Faculty Login
- Faculty Dashboard
- Faculty Profile
- Student List
- Student Profile
- Attendance Monitoring
- Assignment Management
- Assignment Submission Tracking
- Notices
- Timetable
- Reports
- Complaints

### Admin Module

- Admin Login
- Admin Dashboard
- Student Management
- Faculty Management
- System Reports
- User Management
- Role Management

## Technology Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask

### Database
- MySQL

### Development Tools
- Visual Studio Code
- MySQL Server
- Git
- GitHub

## Database

The project uses MySQL database named:

`smart_college`

Main database tables include:

- users
- attendance
- subjects
- assignments
- assignment_submissions
- notices
- timetable
- complaints
- reports
- results

## Project Structure

```text
Smart College Management/
│
├── app.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── attendance.html
│   ├── subjects.html
│   ├── assignments.html
│   ├── notices.html
│   ├── timetable.html
│   ├── result.html
│   ├── complaints.html
│   │
│   ├── faculty_dashboard.html
│   ├── faculty_profile.html
│   ├── faculty_students.html
│   ├── faculty_student_profile.html
│   ├── faculty_attendance.html
│   ├── faculty_assignments.html
│   ├── faculty_assignment_detail.html
│   ├── faculty_notices.html
│   ├── faculty_timetable.html
│   ├── faculty_reports.html
│   └── faculty_complaints.html
│   │
│   ├── admin_dashboard.html
│   ├── admin_students.html
│   ├── admin_edit_student.html
│   ├── admin_faculty.html
│   ├── admin_edit_faculty.html
│   ├── admin_reports.html
│   └── admin_users.html
│
├── static/
│   ├── css/
│   └── js/
│
└── venv/