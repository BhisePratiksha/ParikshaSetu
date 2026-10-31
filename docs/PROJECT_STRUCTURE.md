# ParikshaSetu Project Architecture & Structure

This document outlines the directory structure, design patterns, and architectural responsibilities of each module within the **ParikshaSetu** platform.

---

## 📂 Directory Layout Overview

```text
parikshasetu/
├── app/
│   ├── routes/              # Flask Blueprint route handlers
│   │   ├── __init__.py
│   │   ├── admin.py         # Admin command center & CRUD
│   │   ├── api.py           # Public & protected REST APIs
│   │   ├── auth.py          # Authentication, sessions & RBAC
│   │   ├── exams.py         # Government exam catalog & details
│   │   ├── home.py          # Landing page & platform statistics
│   │   ├── papers.py        # PYQ repository, filters & PDF viewing
│   │   ├── results.py       # CBT scoreboards, reviews & recommendations
│   │   ├── subjects.py      # Police Bharti mandatory subjects & syllabus
│   │   └── tests.py         # CBT test initiation & submission routes
│   │
│   ├── services/            # Business logic and domain services
│   │   ├── __init__.py
│   │   ├── api_import_service.py # JSON Mock API fetch & sync
│   │   ├── paper_service.py      # Paper querying, filtering & distinct values
│   │   ├── pdf_service.py        # PDF file validation, storage & sample generation
│   │   ├── scoring_service.py    # CBT test evaluation, negative marking & weak-area detection
│   │   └── test_service.py       # Test session prep, sanitization & question retrieval
│   │
│   ├── static/              # Static frontend assets
│   │   ├── css/
│   │   │   └── custom.css   # Custom typography, components, and animations
│   │   ├── js/
│   │   │   └── cbt_engine.js # Interactive CBT exam engine & countdown timer
│   │   └── uploads/
│   │       └── pdfs/        # Storage directory for uploaded question papers
│   │
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── admin/           # Admin dashboard, exam/paper managers
│   │   ├── auth/            # Login, registration, profile views
│   │   ├── errors/          # 404 and 500 error pages
│   │   ├── base.html        # Main master layout (Bootstrap 5.3, Navbar, Footer)
│   │   ├── dashboard.html   # Student dashboard & performance history
│   │   ├── exam_details.html
│   │   ├── government_exams.html # Second Main Tab
│   │   ├── home.html        # Platform landing page
│   │   ├── mock_tests.html  # CBT test hub
│   │   ├── paper_details.html # PYQ detail card (4 actions)
│   │   ├── papers.html      # PYQ archive search & filter
│   │   ├── pdf_viewer.html  # In-browser embedded PDF viewer
│   │   ├── police_bharti.html # First Main Tab (5 mandatory subjects)
│   │   ├── results.html     # CBT score card & detailed question breakdown
│   │   ├── solve_paper.html # CBT interface screen
│   │   └── subjects.html    # Subject syllabus & topic overview
│   │
│   ├── __init__.py          # Application Factory (create_app)
│   ├── config.py            # Centralized Configuration class
│   └── extensions.py        # Database proxy, PyMongo adapter & Seed data
│
├── data/                    # Data store & initial seed payloads
│   ├── db_store.json        # High-performance embedded JSON database
│   └── papers.json          # Mock API payload and sample papers
│
├── docs/                    # Technical & operational documentation
│   ├── API_DOCUMENTATION.md
│   ├── DATABASE_SETUP.md
│   ├── ENVIRONMENT_SETUP.md
│   ├── INSTALLATION.md
│   ├── PROJECT_STRUCTURE.md
│   └── TROUBLESHOOTING.md
│
├── tests/                   # Automated test suite
│   ├── __init__.py
│   └── test_app.py          # Integration & unit test cases
│
├── .env                     # Local active environment variables (gitignored)
├── .env.example             # Configuration template
├── .gitignore               # Git exclusion rules
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python package dependencies
├── run.py                   # Development server runner
└── README.md                # Main project documentation
```

---

## 🏛️ Architectural Layers & Patterns

### 1. Application Factory (`app/__init__.py`)
- Employs Flask's Application Factory pattern (`create_app()`).
- Allows dynamic configuration swapping between production, development, and unit testing environments (`TestConfig`).
- Registers all 9 functional Blueprints.
- Injects global template context (navigation exams, current year, bilingual labels).

### 2. Database Proxy & Adapter (`app/extensions.py`)
- Provides `db`, a transparent `DbProxy` that handles switching between:
  - **Live MongoDB**: Connected via `pymongo` with automatic document wrapping (`PyMongoCollectionWrapper` and `PyMongoDatabaseWrapper`) that normalizes ObjectId serialization and ensures compatibility.
  - **Embedded Store**: `MongoCompatibleDatabase` providing MongoDB-like query operations (`$in`, `$regex`, `$or`, `$gte`, `$lte`) backed by `data/db_store.json`.
- Automatic database seeding (`seed_database`) runs on startup if collections are empty.

### 3. Business Service Layer (`app/services/`)
Decouples business logic from HTTP request handlers:
- **`ScoringService`**: Evaluates submitted CBT tests, calculates raw marks and negative penalties, aggregates subject accuracy percentages, and generates actionable weak-area study recommendations.
- **`TestService`**: Prepares test attempts, validates time limits, and **sanitizes question payloads** before sending to the client so answer keys and explanations are never exposed during an active exam.
- **`PaperService`**: Encapsulates paper querying, multi-filter criteria matching, and year/district extraction.
- **`ApiImportService`**: Handles fetching external JSON mock papers, validating structure, logging import runs, and preventing duplicates.
- **`PdfService`**: Handles secure file uploads, PDF validation, and generating fallback sample exam PDFs.

### 4. Interactive Frontend Engine (`app/static/js/cbt_engine.js`)
- Full Computer-Based Test (CBT) engine running in vanilla JavaScript.
- Tracks question states: Answered, Unanswered, Marked for Review.
- Displays an accurate countdown timer with automated submission on time expiry.
- Manages question palette navigation, question jumps, and bilingual English/Marathi toggling.
