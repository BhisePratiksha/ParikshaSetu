# ParikshaSetu Troubleshooting Guide

This document lists common issues, root causes, and verified solutions encountered during setup, development, and execution of the **ParikshaSetu** platform.

---

## 🔍 Index of Common Issues
1. [Missing Dependencies / ModuleNotFoundError](#1-missing-dependencies--modulenotfounderror)
2. [Port Already in Use (`OSError: [Errno 98] / [Errno 10048]`)](#2-port-already-in-use-port-5000)
3. [MongoDB Connection Timeout or Fallback Behavior](#3-mongodb-connection-timeout-or-fallback-behavior)
4. [Missing or Misconfigured `.env` File](#4-missing-or-misconfigured-env-file)
5. [PowerShell Script Execution Policy Error](#5-powershell-script-execution-policy-error)
6. [Pytest Module Collection Error (`No module named 'app'`)](#6-pytest-module-collection-error)
7. [PDF Upload Size Exceeded (`413 Request Entity Too Large`)](#7-pdf-upload-size-exceeded)
8. [JSON Mock API Fetch Timeout or Host Error](#8-json-mock-api-fetch-timeout-or-host-error)

---

### 1. Missing Dependencies / `ModuleNotFoundError`
**Symptom**:
```text
ModuleNotFoundError: No module named 'flask'
# or
ModuleNotFoundError: No module named 'pymongo'
```
**Cause**:
The required Python libraries have not been installed into the active Python environment, or the virtual environment is not activated.

**Solution**:
1. Activate your virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1   # Windows PowerShell
   source .venv/bin/activate       # macOS / Linux
   ```
2. Reinstall all dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

---

### 2. Port Already in Use (Port 5000)
**Symptom**:
```text
OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
```
**Cause**:
Another process (or a previous instance of Flask) is already listening on port `5000`.

**Solution**:
- **Option A: Free port 5000 on Windows**:
  ```powershell
  # Find PID using port 5000
  netstat -ano | findstr :5000
  # Terminate process (replace <PID> with number from rightmost column)
  taskkill /PID <PID> /F
  ```
- **Option B: Run on an alternate port**:
  Open `.env` and set:
  ```env
  PORT=5050
  ```
  Then restart with `python run.py`.

---

### 3. MongoDB Connection Timeout or Fallback Behavior
**Symptom**:
Log displays:
```text
Using high-performance embedded Mongo-compatible JSON store (MongoDB not reachable: ...)
```
**Cause**:
MongoDB service is not installed, not started, or running on a non-standard port.

**Solution**:
- If you intend to use the embedded JSON store: **No action needed!** The application continues to work flawlessly with `data/db_store.json`.
- If you want to use a live MongoDB server:
  1. Start MongoDB on Windows:
     ```powershell
     net start MongoDB
     ```
  2. Verify service is listening on port 27017:
     ```powershell
     python -c "import pymongo; pymongo.MongoClient('mongodb://localhost:27017/').server_info(); print('Connected!')"
     ```

---

### 4. Missing or Misconfigured `.env` File
**Symptom**:
Application uses fallback defaults or fails to find custom configuration settings.

**Solution**:
1. Ensure `.env` exists in the root directory (adjacent to `run.py`):
   ```powershell
   Copy-Item .env.example .env
   ```
2. Verify that variable names match those in `.env.example`.

---

### 5. PowerShell Script Execution Policy Error
**Symptom**:
```text
File ...\.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.
```
**Cause**:
Windows PowerShell script execution policy defaults to `Restricted`.

**Solution**:
Run the following command in PowerShell:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

---

### 6. Pytest Module Collection Error
**Symptom**:
```text
ImportError while importing test module: No module named 'app'
```
**Cause**:
Running `pytest` without the root directory registered in Python's module search path (`sys.path`).

**Solution**:
Ensure `pytest.ini` exists in root with:
```ini
[pytest]
pythonpath = .
testpaths = tests
```
Then run tests with:
```powershell
python -m pytest
# or
pytest
```

---

### 7. PDF Upload Size Exceeded
**Symptom**:
HTTP `413 Request Entity Too Large` when uploading paper PDFs in the admin dashboard.

**Cause**:
Uploaded PDF exceeds `MAX_CONTENT_LENGTH` (default: 16 MB).

**Solution**:
Increase the threshold in `.env`:
```env
# Allow up to 32 MB
MAX_CONTENT_LENGTH=33554432
```

---

### 8. JSON Mock API Fetch Timeout or Host Error
**Symptom**:
Admin JSON Mock Import times out or fails with connection error.

**Cause**:
The external URL configured in `PAPERS_API_URL` is unreachable or blocking requests.

**Solution**:
1. ParikshaSetu has an automatic fallback to local `data/papers.json`.
2. In the Admin Dashboard (**Import Papers** page), check the option to **Import from Local File** (`data/papers.json`), or pass `"force_local": true` to the API.
