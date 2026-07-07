# 🏔 Musafir Treks

A Trekking Management Web Application developed as part of the **Modern Application Development I (MAD-I)** course at IIT Madras.

Musafir Treks is a role-based trekking management system that allows users to discover and book trekking adventures across India while enabling administrators and trek staff to efficiently manage treks, bookings and participants.

The project has been designed with future extensibility in mind and can be enhanced with more advanced AI-based recommendation systems and personalized trekking assistance.
---

# Features

## 👤 User

- User Registration & Login
- Secure password hashing
- Browse available treks
- Search treks by name, location and difficulty
- View trek details
- Live Weather Integration
- AI Trek Recommendation
- Book treks
- Cancel bookings
- Track booking history
- View trekking status
- Budget friendly trek pricing

---

## 👨‍💼 Admin

- Admin Dashboard
- User Management
- Staff Management
- Trek CRUD Operations
- Assign Staff to Treks
- Activate / Deactivate Users & Staff
- Booking Analytics
- Interactive Charts
- Trek Monitoring

---

## 🧭 Trek Staff

- Staff Dashboard
- View Assigned Treks
- Manage Participants
- Update Trek Status
- Request Guide Change
- Occupancy Analytics

---

# Technologies Used

### Backend

- Python
- Flask
- SQLAlchemy
- Flask-Login
- SQLite

### Frontend

- HTML
- CSS
- Bootstrap
- JavaScript
- Jinja2 Templates

### APIs

- OpenWeather API

### Visualization

- Chart.js

---

# Project Structure

```
mad1-trekking-management/

│
├── app.py
├── models.py
├── config.py
├── extensions.py
|
│
├── templates/
│
├── static/
│   ├── images/
│   └── style.css
│
├── instance/
│   └── trekking.db
│
├── requirements.txt
└── README.md
```

---

# Default Login Credentials

## Admin

Email

```
admin@musafir.com
```

Password

```
Musafir@2026Admin
```

---

## Demo Staff

Email

```
staff@musafir.com
```

Password
Musafir@2026Staff
```

```

*(The Demo staff Account exists)*

---

# Installation

Clone the repository

```bash
git clone https://github.com/24f2007162/mad1-trekking-management.git
```

Move into project

```bash
cd mad1-trekking-management
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run application

```bash
python app.py
```

---

# Key Functionalities

- Role Based Authentication
- Secure Password Hashing
- Trek Booking Workflow
- Duplicate Booking Prevention
- Slot Availability Validation
- AI Trek Recommendation
- Weather Integration
- Interactive Analytics Dashboard
- Trek Status Tracking
- Booking History

---

# AI Usage Declaration

AI tools (ChatGPT) were used only as a coding assistant for:

- Debugging
- UI Improvements
- Code Refactoring
- Documentation
- Feature Suggestions

All application logic, implementation, testing and integration were completed and verified by the author.

Approximate AI assistance in this project: **15–20%**

---

# Developed For

Modern Application Development I

Indian Institute of Technology Madras

2026