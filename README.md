# 🎓 Campus360 – College Management System

<p align="center">
  <b>A Role-Based College Management System built with Flask & MySQL</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask">
  <img src="https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge&logo=mysql">
  <img src="https://img.shields.io/badge/HTML5-Frontend-red?style=for-the-badge&logo=html5">
  <img src="https://img.shields.io/badge/CSS3-Styling-blue?style=for-the-badge&logo=css3">
</p>

---

## 📌 About The Project

**Campus360** is a web-based College Management System designed to bring important college activities into one centralized platform.

The system provides separate dashboards for **Students, Faculty, and Administrators**, with features designed according to each user's role.

The project focuses on creating a simple, organized and user-friendly system for managing academic information and college activities.

---

## ✨ Key Features

### 👨‍🎓 Student Module

- 🔐 Secure Login
- 📊 Student Dashboard
- 📅 Attendance Tracking
- 📝 Assignment Management
- 📢 College Notices
- 🗓️ Timetable
- 📚 Academic Results
- 👤 Student Profile
- 💬 Complaint Submission

### 👩‍🏫 Faculty Module

- 🔐 Faculty Login
- 📊 Faculty Dashboard
- 👨‍🎓 Student Management
- 📋 Attendance Management
- 📝 Assignment Management
- 📢 Notice Management
- 🗓️ Faculty Timetable
- 📊 Reports
- 💬 Complaint Management
- 👤 Faculty Profile

### 🛠️ Admin Module

- 🔐 Admin Login
- 📊 Admin Dashboard
- 👨‍🎓 Student Management
- 👩‍🏫 Faculty Management
- 👥 User Management
- 📊 Reports
- ✏️ Edit Student & Faculty Details

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      Campus360       │
                    │ College Management   │
                    │       System         │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       ┌───────────┐     ┌───────────┐     ┌───────────┐
       │  Student  │     │  Faculty  │     │   Admin   │
       └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                     ┌──────────────────┐
                     │   Flask Backend  │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  MySQL Database  │
                     └──────────────────┘
