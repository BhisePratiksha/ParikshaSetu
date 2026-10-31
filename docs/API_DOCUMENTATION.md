# ParikshaSetu REST API Documentation

ParikshaSetu provides RESTful API endpoints for system diagnostics, question paper retrieval, filtering, and administrative JSON mock imports.

---

## 🌐 Base URL
```text
http://127.0.0.1:5000/api
```

---

## 🔒 Authentication & Permissions
- Public endpoints (`GET /api/status`, `GET /api/papers`, `GET /api/papers/<id>`) require no authentication.
- Administrative endpoints (`POST /api/admin/papers/import`) require an authenticated administrator session cookie (`role: 'admin'`).

---

## 📡 Endpoints Specification

### 1. System Health & Diagnostics
Check server uptime, database mode, and collection statistics.

- **URL**: `/api/status`
- **Method**: `GET`
- **Auth Required**: No

#### Response: `200 OK`
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

---

### 2. Get All Papers (With Multi-Criteria Filtering)
Query question papers stored in the platform archive.

- **URL**: `/api/papers`
- **Method**: `GET`
- **Auth Required**: No

#### Optional Query Parameters:
| Parameter | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `exam_id` | `string` | `police-bharti` | Filter by exam identifier. |
| `year` | `integer`| `2025` | Filter by examination year. |
| `district` | `string` | `Pune` | Filter by Maharashtra district. |
| `type` | `string` | `Constable` | Filter by recruitment type. |
| `q` | `string` | `Gramin` | Free-text keyword search. |

#### Example Request:
```http
GET /api/papers?exam_id=police-bharti&year=2025 HTTP/1.1
Host: 127.0.0.1:5000
Accept: application/json
```

#### Response: `200 OK`
```json
{
  "status": "success",
  "total_papers": 1,
  "papers": [
    {
      "id": "pb-2025-pune",
      "exam_id": "police-bharti",
      "title": "Maharashtra Police Bharti 2025 - Pune Gramin Constable",
      "title_mr": "महाराष्ट्र पोलीस भरती २०२५ - पुणे ग्रामीण पोलीस शिपाई",
      "year": 2025,
      "district": "Pune (पुणे)",
      "recruitment_type": "Police Constable",
      "total_questions": 100,
      "total_marks": 100,
      "pdf_url": "/static/uploads/pdfs/pb-2025-pune.pdf",
      "is_solved": true
    }
  ]
}
```

---

### 3. Get Single Paper Details
Fetch full metadata for a specific paper including linked exam information.

- **URL**: `/api/papers/<paper_id>`
- **Method**: `GET`
- **Auth Required**: No

#### Path Parameters:
- `paper_id` *(string)*: Unique identifier of the paper (e.g. `pb-2025-pune`).

#### Example Request:
```http
GET /api/papers/pb-2025-pune HTTP/1.1
Host: 127.0.0.1:5000
Accept: application/json
```

#### Response: `200 OK`
```json
{
  "status": "success",
  "paper": {
    "id": "pb-2025-pune",
    "exam_id": "police-bharti",
    "title": "Maharashtra Police Bharti 2025 - Pune Gramin Constable",
    "year": 2025,
    "district": "Pune (पुणे)",
    "pdf_url": "/static/uploads/pdfs/pb-2025-pune.pdf"
  },
  "exam": {
    "id": "police-bharti",
    "name": "Maharashtra Police Bharti",
    "duration_minutes": 90,
    "negative_marks": 0.0
  }
}
```

#### Error Response: `404 Not Found`
```json
{
  "error": "Paper not found",
  "status": "error"
}
```

---

### 4. Import Papers via External Mock API / Local File
Trigger sync from external `PAPERS_API_URL` or fallback `data/papers.json`.

- **URL**: `/api/admin/papers/import`
- **Method**: `POST`
- **Auth Required**: Yes (Admin session cookie required)
- **Headers**:
  ```http
  Content-Type: application/json
  ```

#### Optional JSON Body:
```json
{
  "url": "https://raw.githubusercontent.com/sample/parikshasetu/main/data/papers.json",
  "force_local": false
}
```

#### Response: `200 OK`
```json
{
  "success": true,
  "source": "https://raw.githubusercontent.com/sample/parikshasetu/main/data/papers.json",
  "total_processed": 6,
  "inserted": 0,
  "updated": 6,
  "errors": [],
  "timestamp": "2026-11-01T00:50:00.000Z"
}
```

---

## 📮 Testing APIs with Postman or cURL

### cURL Examples

#### 1. Test System Health:
```powershell
curl -X GET http://127.0.0.1:5000/api/status
```

#### 2. Query Papers:
```powershell
curl -X GET "http://127.0.0.1:5000/api/papers?exam_id=police-bharti"
```

### Postman Setup Steps:
1. Open **Postman** and create a new Collection named `ParikshaSetu`.
2. Add a request `GET http://127.0.0.1:5000/api/status`. Send and inspect the JSON output.
3. Add a request `GET http://127.0.0.1:5000/api/papers`. Under the **Params** tab, add keys `exam_id` and `year`.
4. For protected admin endpoints, first perform a `POST http://127.0.0.1:5000/auth/login` with form-data `email=admin@parikshasetu.com` and `password=Admin@123`. Postman will automatically capture and persist the session cookie.
