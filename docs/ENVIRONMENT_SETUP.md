# ParikshaSetu Environment Setup Guide

This document describes all environment variables used by the **ParikshaSetu** platform, how to configure `.env` files, database settings, and production considerations.

---

## 🔑 Environment Variable Reference

The application loads configuration parameters through `python-dotenv` from the `.env` file located in the root directory.

| Variable Name | Default Value | Required | Description |
| :--- | :--- | :---: | :--- |
| `FLASK_APP` | `run.py` | No | Entrypoint script for Flask CLI commands. |
| `FLASK_ENV` | `development` | No | Environment mode (`development`, `production`, or `testing`). |
| `FLASK_DEBUG` | `1` | No | Enables hot reload and interactive tracebacks (`1` for ON, `0` for OFF). |
| `SECRET_KEY` | `parikshasetu-secret-key-2026-production` | **Yes (Prod)** | Cryptographic secret used for session cookie signing and CSRF tokens. |
| `MONGO_URI` | `mongodb://localhost:27017/parikshasetu_db` | No | MongoDB connection connection string (supports standalone or MongoDB Atlas). |
| `MONGO_DB_NAME` | `parikshasetu_db` | No | Database name to use within MongoDB. |
| `PAPERS_API_URL` | `https://your-hosted-domain.com/papers.json` | No | Configurable URL for external JSON mock paper import service. |
| `ADMIN_EMAIL` | `admin@parikshasetu.com` | No | Email address for auto-seeded super administrator account. |
| `ADMIN_PASSWORD` | `Admin@123` | No | Initial default password for administrator login. |
| `ADMIN_NAME` | `System Administrator` | No | Display name for system administrator. |
| `PORT` | `5000` | No | HTTP server port for development and local testing. |
| `HOST` | `127.0.0.1` | No | Network interface address to bind (`0.0.0.0` for all interfaces). |
| `UPLOAD_FOLDER` | `app/static/uploads/pdfs` | No | Relative or absolute path where question paper PDFs are stored. |
| `MAX_CONTENT_LENGTH`| `16777216` | No | Maximum allowed file upload size in bytes (default: 16 MB). |

---

## 🛠️ Configuring `.env` and `.env.example`

### 1. The Template File (`.env.example`)
The `.env.example` file is tracked in version control and acts as a contract for all developers. It contains placeholders and example values:

```env
# Flask Environment Configuration
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=change_me_to_a_secure_random_key

# MongoDB Connection
MONGO_URI=mongodb://localhost:27017/parikshasetu_db
MONGO_DB_NAME=parikshasetu_db

# External Papers Mock API URL
PAPERS_API_URL=https://your-hosted-domain.com/papers.json

# Admin Account Defaults
ADMIN_EMAIL=admin@parikshasetu.com
ADMIN_PASSWORD=Admin@123
ADMIN_NAME=System Administrator

# Server Settings
PORT=5000
HOST=127.0.0.1
UPLOAD_FOLDER=app/static/uploads/pdfs
MAX_CONTENT_LENGTH=16777216
```

### 2. Generating Secure Secret Keys
For staging and production environments, generate a cryptographically strong `SECRET_KEY` using Python:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Then copy the generated 64-character token into your `.env` file:
```env
SECRET_KEY=e83bf61298492040...
```

---

## 🗄️ Database Connection Settings

ParikshaSetu offers a **dual-mode database architecture**:

### Mode A: Local or Remote MongoDB (Recommended for Production)
1. If you run a local MongoDB instance, ensure MongoDB service is started:
   ```powershell
   net start MongoDB
   ```
2. Set `MONGO_URI`:
   ```env
   MONGO_URI=mongodb://localhost:27017/parikshasetu_db
   ```
3. For **MongoDB Atlas (Cloud)**:
   ```env
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/parikshasetu_db?retryWrites=true&w=majority
   ```

### Mode B: Zero-Configuration Embedded JSON Store (Fallback)
If MongoDB is not installed or unreachable, the application automatically catches the connection timeout and boots using `MongoCompatibleDatabase` backed by `data/db_store.json`.
- No separate database installation or configuration is needed.
- Data persists across server restarts in `data/db_store.json`.

---

## 🌐 External Mock API Endpoint Configuration

The platform supports ingesting question papers from external repositories via HTTP GET:
- By default, `PAPERS_API_URL` is set to an external endpoint or raw GitHub URL.
- If external connectivity is unavailable or network times out (8-second timeout), the platform seamlessly falls back to `data/papers.json`.

---

## 🛡️ Security Best Practices
- **Never commit `.env` to git.** `.env` is listed in `.gitignore`.
- Change default admin passwords (`Admin@123`) before public deployment.
- Keep `FLASK_DEBUG=0` in production environments.
- Serve through a production WSGI server such as `Gunicorn` or `Waitress` behind Nginx/Caddy with SSL/TLS.
