# ParikshaSetu (परीक्षामार्ग) — Government Exam Preparation Platform

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-MongoDB%20%2F%20Embedded%20JSON-brightgreen.svg)](https://www.mongodb.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Bootstrap%205.3%20%7C%20Vanilla%20JS-purple.svg)](https://getbootstrap.com/)
[![Tests](https://img.shields.io/badge/Tests-11%2F11%20Passing-success.svg)](https://pytest.org/)

**ParikshaSetu (परीक्षामार्ग)** is an end-to-end, production-grade, responsive web platform engineered specifically for candidates preparing for Maharashtra State and Central Government competitive examinations.

It delivers specialized preparation hubs for **Maharashtra Police Bharti (महाराष्ट्र पोलीस भरती)**, **MPSC Group B & C**, **Maharashtra Talathi Bharti (TCS Pattern)**, **Zilla Parishad (ZP) Bharti (IBPS Pattern)**, **SSC (Staff Selection Commission)**, **Railway Recruitment Board (RRB)**, and **Banking Exams (IBPS/SBI)**.

---

## 📑 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features & Functionalities](#-key-features--functionalities)
3. [Technology Stack](#-technology-stack)
4. [Prerequisites](#-prerequisites)
5. [Project Architecture & Structure](#-project-architecture--structure)
6. [Environment Setup & Configuration](#-environment-setup--configuration)
7. [Installation Guide](#-installation-guide)
8. [How to Run the Application](#-how-to-run-the-application)
9. [Default Login Credentials](#-default-login-credentials)
10. [REST API Documentation](#-rest-api-documentation)
11. [Troubleshooting Guide](#-troubleshooting-guide)
12. [Additional Documentation](#-additional-documentation)

---

## 🌟 Project Overview

### Purpose & Objectives
The mission of **ParikshaSetu** is to eliminate fragmented, outdated exam preparation materials by providing government exam aspirants with an authentic, unified digital environment.
- **Police Bharti Focus**: Solves the syllabus fragmentation by establishing a primary dedicated dashboard for the 5 mandatory Police Bharti subjects.
- **Authentic PYQ Archive**: Connects users to official previous-year question papers with multi-criteria filtering by year, district, and exam type.
- **Interactive CBT Mock Exams**: Replicates actual Computer-Based Test (CBT) examination interfaces (TCS & IBPS patterns) with instant scoring and negative marking.
- **AI-Powered Weak Area Insights**: Diagnoses candidate performance down to the subject level and delivers targeted recommendations.
- **Zero-Friction Deployment**: Dual-mode persistence layer ensures the platform runs instantly out-of-the-box with or without a standalone MongoDB server.

---

## 🏛️ Key Features & Functionalities

### 1. First Main Tab — Maharashtra Police Bharti (महाराष्ट्र पोलीस भरती)
Dedicated dashboard covering all 5 mandatory examination subjects:
- **मराठी व्याकरण (Marathi Grammar)**: वर्णविचार, नाम, सर्वनाम, विशेषण, क्रियापद, काळ, प्रयोग, समास, समानार्थी व विरुद्धार्थी शब्द.
- **सामान्य ज्ञान (General Knowledge)**: महाराष्ट्राचा इतिहास, भूगोल, राज्यघटना, पंचायत राज, विज्ञान आणि पोलीस प्रशासन (SID/CID).
- **चालू घडामोडी (Current Affairs)**: राज्य व राष्ट्रीय योजना, क्रीडा घडामोडी, आंतरराष्ट्रीय पुरस्कार.
- **बुद्धिमत्ता चाचणी (Reasoning / Intelligence Test)**: संख्या मालिका, सांकेतिक भाषा, नातेसंबंध, दिशाज्ञान, घड्याळ व दिनदर्शिका.
- **अंकगणित (Arithmetic / Mathematics)**: संख्याज्ञान, लसावि-मसावि, सरासरी, शेकडेवारी, नफा-तोटा, काळ-काम-वेग आणि सरळव्याज.
Each subject features topic-wise syllabus breakdowns, practice questions, and direct links to authentic solved question papers.

### 2. Second Main Tab — Government Exams (शासकीय स्पर्धा परीक्षा)
Isolated dashboards and syllabus structures for:
- **MPSC Group B & C Combine** (PSI, STI, ASO, Tax Assistant)
- **Maharashtra Talathi Bharti** (TCS Exam Pattern)
- **Zilla Parishad (ZP) Bharti** (Gramsevak, Arogya Sevak)
- **SSC** (GD Constable, CGL, CHSL)
- **Railway Recruitment Board (RRB)** (NTPC, ALP, Group D)
- **Banking Exams** (IBPS, SBI, RBI Assistant)

### 3. Previous-Year Question Paper (PYQ) Repository
- Hierarchical Discovery: `Exam Category → Select Exam → Select Year → Select Paper`.
- Multi-Criteria Real-Time Filters: **Year, District, Recruitment Type, and Text Search**.
- **4 Core Actions per Paper**:
  1. 👁️ **View PDF**: In-browser embedded PDF viewer with fallback download links.
  2. 📥 **Download PDF**: Direct download for offline study.
  3. 🔑 **View Answer Key**: Official verified answer key modal.
  4. ⚡ **Solve Online**: Interactive timed CBT exam session.

### 4. Interactive CBT Examination Engine
- Full-screen timed interface matching official testing agency consoles.
- Dynamic question palette: Answered, Unanswered, and Marked for Review indicators.
- Real-time countdown timer with automatic submission on expiration.
- Bilingual Question Display: Instant toggle between Marathi (मराठी) and English.
- Server-side security: Correct answers and explanations are never sent to the client during active test sessions.

### 5. Instant Results & Performance Analytics
- Automatic server-side evaluation including negative marking deductions.
- Key metrics: Total Questions, Attempted, Correct, Incorrect, Score, and Percentage.
- Subject-wise accuracy breakdown matrix.
- Rule-based study recommendations identifying candidate's weakest topics.
- Full post-test review with official answers and detailed explanations.

### 6. Admin Command Center
- Role-Based Access Control (`admin` vs `student`).
- Exam CRUD: Manage exam durations, total marks, and negative marking penalty ratios.
- Paper Manager: Create and update papers with PDF upload capabilities.
- Mock API Import Engine: On-demand sync with external JSON endpoints or local backup files.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend Framework** | **Python 3.10+ / 3.14+**, **Flask 3.1**, **Jinja2 Templates**, **Werkzeug 3.1** |
| **Frontend UI** | **HTML5**, **Vanilla CSS3**, **Bootstrap 5.3**, **Bootstrap Icons**, **JavaScript (ES6+)** |
| **Database** | **MongoDB 6.0 – 9.0+** (`parikshasetu_db`) via `pymongo` **OR** built-in **MongoCompatibleStore** (`data/db_store.json`) |
| **API & Networking** | **Requests 2.34+**, **RESTful JSON Endpoints** |
| **Testing** | **unittest**, **pytest 9.2+**, **mongomock 4.3+** |
| **Configuration** | **python-dotenv 1.2+** |

---

## 📋 Prerequisites

Before installing the application, ensure the following software is present on your workstation:

1. **Python**: Version `3.10.0` or newer (Tested up to Python `3.14.7`). Verify with:
   ```powershell
   python --version
   ```
2. **pip**: Python package manager. Verify with:
   ```powershell
   pip --version
   ```
3. **MongoDB** *(Optional)*: Community Server `5.0+` to `9.0+`.
   > *Note: If MongoDB is not installed, ParikshaSetu automatically activates its embedded JSON store fallback. No setup is blocked.*
4. **Git**: Version control client.
5. **Modern Web Browser**: Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari.
6. **Recommended IDE**: Visual Studio Code, Cursor, or PyCharm with Python and HTML/CSS extensions.

---

## 📂 Project Architecture & Structure

```text
parikshasetu/
├── app/
│   ├── routes/              # Flask Blueprint route controllers
│   │   ├── admin.py         # Admin command center, CRUD operations, and Mock imports
│   │   ├── api.py           # Public and protected REST APIs (/api/status, /api/papers)
│   │   ├── auth.py          # User registration, login, logout, profile
│   │   ├── exams.py         # Government exam catalog & details
│   │   ├── home.py          # Platform landing page & live statistics
│   │   ├── papers.py        # Question paper repository, multi-filters & PDF view
│   │   ├── results.py       # CBT scorecards, analytics & weak-area recommendations
│   │   ├── subjects.py      # Police Bharti mandatory 5 subjects & topics
│   │   └── tests.py         # CBT exam initialization, question delivery & submission
│   │
│   ├── services/            # Encapsulated domain business logic
│   │   ├── api_import_service.py # JSON Mock API fetch, validation & audit logging
│   │   ├── paper_service.py      # Paper querying, filtering & distinct metadata
│   │   ├── pdf_service.py        # PDF upload validation & sample file generator
│   │   ├── scoring_service.py    # Test evaluation, negative marking & analysis
│   │   └── test_service.py       # CBT question preparation & client-side sanitization
│   │
│   ├── static/              # Frontend static resources
│   │   ├── css/custom.css   # Custom styling, responsive badges & layout rules
│   │   ├── js/cbt_engine.js # Interactive CBT exam engine & countdown timer
│   │   └── uploads/pdfs/    # Storage folder for question paper PDF files
│   │
│   ├── templates/           # Jinja2 HTML views
│   │   ├── admin/           # Administrative interfaces
│   │   ├── auth/            # Authentication forms
│   │   ├── errors/          # 404 & 500 error pages
│   │   ├── base.html        # Master layout (Navigation, Footer, Global Assets)
│   │   ├── home.html        # Landing page
│   │   ├── police_bharti.html # Police Bharti primary tab (5 subjects)
│   │   ├── government_exams.html # Government exams tab
│   │   ├── papers.html      # PYQ archive search and filter interface
│   │   ├── paper_details.html # Paper detail view (4 actions)
│   │   ├── pdf_viewer.html  # In-browser embedded PDF viewer
│   │   ├── solve_paper.html # Interactive CBT testing room
│   │   └── results.html     # Scorecard, question breakdown & recommendations
│   │
│   ├── __init__.py          # Application Factory (create_app)
│   ├── config.py            # Central configuration class
│   └── extensions.py        # Database proxy, PyMongo adapter & automatic seed data
│
├── data/                    # Storage for persistent data & seed payloads
│   ├── db_store.json        # High-performance embedded JSON database
│   └── papers.json          # Mock API payload and sample papers
│
├── docs/                    # In-depth technical documentation
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SETUP.md
│   ├── ENVIRONMENT_SETUP.md
│   ├── INSTALLATION.md
│   ├── PROJECT_STRUCTURE.md
│   └── TROUBLESHOOTING.md
│
├── tests/                   # Automated test suite
│   └── test_app.py          # 11 unit & integration test cases
│
├── .env                     # Local environment settings (gitignored)
├── .env.example             # Environment template
├── .gitignore               # Git exclusion list
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python package dependencies
├── run.py                   # Application entrypoint runner
└── README.md                # Project documentation
```

---

## ⚙️ Environment Setup & Configuration

### 1. Creating the `.env` Configuration File
Copy the provided `.env.example` file to create your active `.env`:

#### On Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

#### On macOS / Linux:
```bash
cp .env.example .env
```

### 2. Environment Variables Specification

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `FLASK_APP` | `run.py` | Flask entrypoint file. |
| `FLASK_ENV` | `development` | Environment mode (`development` or `production`). |
| `FLASK_DEBUG` | `1` | Enables debug mode and hot reloading (`1` = ON, `0` = OFF). |
| `SECRET_KEY` | *(Set strong key)* | Session signing secret key. |
| `MONGO_URI` | `mongodb://localhost:27017/parikshasetu_db` | Connection URI for MongoDB instance. |
| `MONGO_DB_NAME` | `parikshasetu_db` | Database name. |
| `PAPERS_API_URL`| `https://raw.githubusercontent.com/...` | Endpoint for external JSON mock paper import. |
| `ADMIN_EMAIL` | `admin@parikshasetu.com` | Default super administrator email. |
| `ADMIN_PASSWORD` | `Admin@123` | Default super administrator password. |
| `ADMIN_NAME` | `System Administrator` | Default administrator name. |
| `PORT` | `5000` | Port for the web server. |
| `HOST` | `127.0.0.1` | Network interface to bind. |
| `MAX_CONTENT_LENGTH` | `16777216` | Maximum file upload size in bytes (16 MB). |

---

## 🚀 Installation Guide

Follow these exact steps to install and set up the project from scratch:

### Step 1: Open Terminal in Project Directory
```powershell
cd C:\Users\Pratiksha\.gemini\antigravity-ide\scratch\parikshasetu
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment named .venv
python -m venv .venv

# Activate on Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# (If using macOS / Linux):
# source .venv/bin/activate
```

### Step 3: Upgrade pip and Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```powershell
Copy-Item .env.example .env
```

### Step 5: Run Automated Tests
Ensure all 11 unit and integration tests pass:
```powershell
# Run with Python unittest:
python -m unittest tests/test_app.py

# Or run with pytest:
pytest
```

---

## 💻 How to Run the Application

### 1. Database Server (Optional)
- **If using MongoDB**: Ensure the MongoDB service is active:
  ```powershell
  net start MongoDB
  ```
- **If not using MongoDB**: No action required! The embedded JSON store starts automatically.

### 2. Application Server (Backend + Frontend)
ParikshaSetu renders server-side Jinja2 templates and dynamic JavaScript CBT client bundles concurrently through Flask:

```powershell
python run.py
```

Console Output:
```text
========================================================
ParikshaSetu Government Exam Preparation Platform
Server running at: http://127.0.0.1:5000/
Admin login: admin@parikshasetu.com / Admin@123
Student login: student@parikshasetu.com / Student@123
========================================================
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 🔑 Default Login Credentials

The database automatically seeds standard user credentials on initial boot:

| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@parikshasetu.com` | `Admin@123` | Full Admin Dashboard, Manage Exams, Question Papers, PDF Uploads, Mock API Sync |
| **Candidate / Student** | `student@parikshasetu.com` | `Student@123` | Interactive CBT Exams, Question Bank, Results, Personal Analytics |

---

## 🌐 REST API Documentation

ParikshaSetu exposes clean RESTful JSON endpoints for platform status and question papers:

### 1. `GET /api/status`
Returns application diagnostics, database status, and catalog counts.
```powershell
curl -X GET http://127.0.0.1:5000/api/status
```
**Sample Response (`200 OK`)**:
```json
{
  "application": "ParikshaSetu Government Exam Preparation Platform",
  "database": "MongoDB / MongoCompatibleStore",
  "status": "success",
  "total_exams": 7,
  "total_papers": 6,
  "total_questions": 7,
  "version": "1.0.0"
}
```

### 2. `GET /api/papers`
Returns archived question papers with optional query filters:
- `?exam_id=police-bharti`
- `?year=2025`
- `?district=Pune`
- `?q=Gramin`

```powershell
curl -X GET "http://127.0.0.1:5000/api/papers?exam_id=police-bharti&year=2025"
```

### 3. `GET /api/papers/<paper_id>`
Returns specific paper metadata, PDF download URL, and exam attributes.

### 4. `POST /api/admin/papers/import`
*(Protected: Admin Session Required)* Synchronizes paper metadata from `PAPERS_API_URL` or local backup.

For complete API parameters, schemas, and Postman setup steps, see [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md).

---

## 🔧 Troubleshooting Guide

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'flask'` | Dependencies not installed or virtual environment inactive. | Run `.\.venv\Scripts\Activate.ps1` and `pip install -r requirements.txt`. |
| `OSError: [WinError 10048] Only one usage of each socket address...` | Port `5000` is currently occupied by another process. | Kill the process using port 5000 (`netstat -ano \| findstr :5000` then `taskkill /PID <PID> /F`) or change `PORT=5050` in `.env`. |
| `Using high-performance embedded Mongo-compatible JSON store...` | MongoDB server is not running locally. | **Normal behavior.** Application operates seamlessly using `data/db_store.json`. To use MongoDB, start the service with `net start MongoDB`. |
| `ImportError: No module named 'app'` during pytest | Python search path missing root directory. | Ensure `pytest.ini` exists with `pythonpath = .` and run `pytest`. |
| `413 Request Entity Too Large` | Uploaded PDF exceeds configured max size. | Increase `MAX_CONTENT_LENGTH` in `.env` (e.g., `33554432` for 32 MB). |
| PowerShell script execution disabled error | Windows default script security policy. | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell window. |

For additional troubleshooting scenarios, consult [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

---

## 📚 Additional Documentation

Detailed operational and architectural guides are available in the [`docs/`](docs/) directory:

- 📖 [**Installation Guide (`docs/INSTALLATION.md`)**](docs/INSTALLATION.md) — Comprehensive installation walkthrough.
- ⚙️ [**Environment Setup (`docs/ENVIRONMENT_SETUP.md`)**](docs/ENVIRONMENT_SETUP.md) — Environment variables, secrets, and modes.
- 🏛️ [**Project Architecture (`docs/PROJECT_STRUCTURE.md`)**](docs/PROJECT_STRUCTURE.md) — Directory layout and service layer responsibilities.
- 🌐 [**REST API Documentation (`docs/API_DOCUMENTATION.md`)**](docs/API_DOCUMENTATION.md) — Endpoints, payloads, and Postman examples.
- 🗄️ [**Database Setup (`docs/DATABASE_SETUP.md`)**](docs/DATABASE_SETUP.md) — MongoDB installation, Atlas setup, and seeding.
- 🔍 [**Troubleshooting Manual (`docs/TROUBLESHOOTING.md`)**](docs/TROUBLESHOOTING.md) — Common error messages and solutions.

---

## 📄 License
This project is open-source and developed for competitive examination aspirants and educational institutions.
