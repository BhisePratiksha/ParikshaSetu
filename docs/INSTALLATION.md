# ParikshaSetu Installation Guide

This document provides a comprehensive, step-by-step guide to installing, configuring, and verifying the **ParikshaSetu** platform on your development workstation (Windows, macOS, or Linux).

---

## 📋 System Prerequisites

Ensure the following tools and runtimes are installed on your system before proceeding:

| Software / Runtime | Recommended Version | Minimum Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Python** | 3.11.x – 3.14.x | 3.10.0 | Backend runtime and execution engine |
| **pip** | Latest | 23.0+ | Python package manager |
| **MongoDB** *(Optional)* | 6.0 – 9.0+ | 5.0.0 | Primary document database (embedded fallback available) |
| **Git** | 2.40+ | 2.20+ | Version control system |
| **Web Browser** | Latest Chrome / Edge / Firefox | Modern ECMAScript 6+ | CBT testing interface and admin dashboard |

> [!NOTE]
> **Zero-Setup Database Fallback:** ParikshaSetu includes a built-in `MongoCompatibleDatabase` backed by `data/db_store.json`. If you do not have MongoDB installed or running, the platform operates seamlessly without requiring manual database installation.

---

## 🚀 Step-by-Step Installation Instructions

### Step 1: Clone or Open the Repository

Open your terminal (PowerShell or Command Prompt on Windows, Bash on macOS/Linux) and navigate to your workspace:

```powershell
# If cloning via Git:
git clone https://github.com/your-username/parikshasetu.git
cd parikshasetu

# Or open your existing project folder:
cd C:\Users\Pratiksha\.gemini\antigravity-ide\scratch\parikshasetu
```

---

### Step 2: Set Up a Python Virtual Environment

It is strongly recommended to use an isolated Python virtual environment to manage dependencies cleanly.

#### On Windows (PowerShell):
```powershell
# 1. Create a virtual environment named .venv
python -m venv .venv

# 2. Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# If PowerShell execution policy restricts scripts, run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

#### On Windows (Command Prompt `cmd`):
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

#### On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Step 3: Install Required Dependencies

Upgrade `pip` and install all application packages from `requirements.txt`:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Dependencies Installed:
- **Flask (>=3.0.0)**: Lightweight WSGI web application framework.
- **pymongo (>=4.6.0)**: Official Python driver for MongoDB.
- **python-dotenv (>=1.0.0)**: Loads environment variables from `.env`.
- **Werkzeug (>=3.0.0)**: Security utilities, password hashing, and WSGI tools.
- **requests (>=2.31.0)**: HTTP library for JSON Mock API sync and paper fetching.
- **mongomock (>=4.1.2)**: MongoDB in-memory mock library for testing.
- **pytest (>=8.0.0)**: Automated test execution framework.

---

### Step 4: Configure Environment Variables

Create your local `.env` configuration file from the provided `.env.example` template:

#### On Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

#### On macOS / Linux / Bash:
```bash
cp .env.example .env
```

Open `.env` in your text editor and review the parameters (such as `SECRET_KEY`, `MONGO_URI`, and `PORT`). For complete variable descriptions, consult [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md).

---

### Step 5: Verify Static Assets and Uploads Directory

The application dynamically manages uploads and sample PDF question papers inside `app/static/uploads/pdfs/`. The initialization routine verifies and populates these directories automatically upon first launch.

---

### Step 6: Run Automated Verification Tests

Verify that all modules, route handlers, scoring algorithms, and API endpoints are functional:

```powershell
# Using Python's built-in unittest:
python -m unittest tests/test_app.py

# Or using pytest:
pytest
```

Expected result:
```text
Ran 11 tests in 0.612s
OK
```

---

### Step 7: Launch the Development Server

Start the ParikshaSetu application:

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
**[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**
