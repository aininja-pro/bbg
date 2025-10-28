# API Reference

Complete reference for all backend API endpoints in the BBG Rebate Processing Tool.

## Base URL

**Local Development:** `http://localhost:8001`
**Production:** `[Your production URL]`

## Interactive API Documentation

FastAPI provides interactive API documentation at:
- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

You can test all endpoints directly from these interfaces.

---

## File Processing APIs

### POST /api/upload

Upload and process a single Excel file, returns preview data.

**Request:**
```http
POST /api/upload
Content-Type: multipart/form-data

file: [Excel file binary]
```

**Parameters:**
- `file` (form-data, required): Excel file (.xlsm or .xlsx)

**Response:**
```json
{
  "success": true,
  "data": {
    "preview": [
      {
        "member_name": "Bosgraaf Homes",
        "bbg_member_id": "1003",
        "confirmed_occupancy": "7/2/25",
        ...
      }
    ],
    "total_rows": 1380,
    "member_name": "Bosgraaf Homes",
    "bbg_member_id": "1003"
  }
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid file type or size
- `500`: Processing error

---

### POST /api/process-and-download

Process file and return downloadable CSV.

**Request:**
```http
POST /api/process-and-download
Content-Type: multipart/form-data

file: [Excel file binary]
```

**Response:**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="[filename]_processed.csv"

[CSV file binary]
```

**Status Codes:**
- `200`: Success, returns CSV file
- `400`: Invalid file
- `500`: Processing error

---

### POST /api/upload-with-cache

Upload and process file with caching for instant downloads.

**Request:**
```http
POST /api/upload-with-cache
Content-Type: multipart/form-data

file: [Excel file binary]
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "filename": "original_file.xlsm",
  "created_at": "2025-10-27T20:00:00",
  "row_count": 1380
}
```

---

### POST /api/batch-process

Process multiple files and return merged CSV or ZIP.

**Request:**
```http
POST /api/batch-process?output_mode=merged
Content-Type: multipart/form-data

files: [Excel file 1]
files: [Excel file 2]
...
```

**Parameters:**
- `output_mode` (query, required): `"merged"` or `"zip"`
- `files` (form-data, required): Multiple Excel files

**Response:**
- **merged mode**: Returns single CSV file
- **zip mode**: Returns ZIP file containing individual CSVs

---

### POST /api/batch-process-with-cache

Batch process with caching support.

**Request:**
```http
POST /api/batch-process-with-cache?output_mode=merged
Content-Type: multipart/form-data

files: [Multiple Excel files]
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "filename": "batch_output",
  "created_at": "2025-10-27T20:00:00",
  "file_count": 10
}
```

---

### GET /api/download/{job_id}

Download cached processed file by job ID.

**Request:**
```http
GET /api/download/{job_id}
```

**Response:**
- CSV or ZIP file binary

---

### GET /api/job-status/{job_id}

Check status of a cached job.

**Request:**
```http
GET /api/job-status/{job_id}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "filename": "file.xlsm",
  "created_at": "2025-10-27T20:00:00"
}
```

---

### DELETE /api/cleanup-expired

Clean up expired cached files (admin endpoint).

**Request:**
```http
DELETE /api/cleanup-expired
```

**Response:**
```json
{
  "deleted_count": 5,
  "message": "Cleaned up 5 expired files"
}
```

---

## Business Rules APIs

### GET /api/rules

Get all business rules.

**Request:**
```http
GET /api/rules
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Map Day & Night to Carrier",
    "priority": 1,
    "enabled": true,
    "config": {
      "condition": {
        "supplier_name_equals": "Day & Night Heating & Cooling"
      },
      "set_supplier": "Carrier"
    },
    "created_at": "2025-10-27T12:00:00",
    "updated_at": "2025-10-27T12:00:00"
  }
]
```

---

### GET /api/rules/{rule_id}

Get a single rule by ID.

**Request:**
```http
GET /api/rules/1
```

**Response:**
```json
{
  "id": 1,
  "name": "Map Day & Night to Carrier",
  ...
}
```

---

### POST /api/rules

Create a new business rule.

**Request:**
```http
POST /api/rules
Content-Type: application/json

{
  "name": "New Rule",
  "priority": 5,
  "enabled": true,
  "config": {
    "condition": {
      "product_id_contains": "5534"
    },
    "set_supplier": "Air Vent"
  }
}
```

**Response:**
```json
{
  "id": 9,
  "name": "New Rule",
  ...
}
```

---

### PUT /api/rules/{rule_id}

Update an existing rule.

**Request:**
```http
PUT /api/rules/1
Content-Type: application/json

{
  "enabled": false
}
```

**Response:**
```json
{
  "id": 1,
  "enabled": false,
  ...
}
```

---

### DELETE /api/rules/{rule_id}

Delete a rule.

**Request:**
```http
DELETE /api/rules/1
```

**Response:**
```
204 No Content
```

---

### POST /api/rules/reorder

Reorder rules by updating priorities.

**Request:**
```http
POST /api/rules/reorder
Content-Type: application/json

{
  "rule_ids": [3, 1, 2, 4]
}
```

---

## Lookup Tables APIs

### Members

#### GET /api/lookups/members

Get all members.

**Response:**
```json
[
  {
    "id": 1,
    "member_name": "Bosgraaf Homes",
    "bbg_member_id": "1003",
    "created_at": "2025-10-27T12:00:00"
  }
]
```

#### GET /api/lookups/members/{member_id}

Get single member.

#### POST /api/lookups/members

Create new member.

**Request:**
```json
{
  "member_name": "New Member LLC",
  "bbg_member_id": "1999"
}
```

#### PUT /api/lookups/members/{member_id}

Update member.

#### DELETE /api/lookups/members/{member_id}

Delete member.

#### POST /api/lookups/members/bulk-upload

Upload CSV to replace all members.

**Request:**
```http
POST /api/lookups/members/bulk-upload
Content-Type: multipart/form-data

file: [CSV file]
```

**CSV Format:**
```csv
member_name,bbg_member_id
Bosgraaf Homes,1003
New Tradition Homes,1564
```

---

### Suppliers

#### GET /api/lookups/suppliers

Get all suppliers.

#### POST /api/lookups/suppliers

Create new supplier.

**Request:**
```json
{
  "supplier_name": "Carrier",
  "tradenet_supplier_id": "5001"
}
```

#### POST /api/lookups/suppliers/bulk-upload

Upload CSV to replace all suppliers.

**CSV Format:**
```csv
supplier_name,tradenet_supplier_id
Carrier,5001
CertainTeed,5002
```

---

### Products

#### GET /api/lookups/products

Get all products (if using database products).

#### POST /api/lookups/products

Create product.

**Note:** Products are currently extracted from uploaded files, not stored in database.

---

## Health Check APIs

### GET /

Root health check.

**Response:**
```json
{
  "status": "online",
  "service": "BBG Rebate Processing API",
  "version": "0.1.0"
}
```

### GET /health

Detailed health check.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "services": {
    "api": "running",
    "file_processing": "ready"
  }
}
```

---

## Error Responses

All endpoints may return these error formats:

**400 Bad Request:**
```json
{
  "detail": "Invalid file type. Only .xlsm and .xlsx files are supported."
}
```

**404 Not Found:**
```json
{
  "detail": "Rule with id 999 not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "An internal server error occurred"
}
```

---

## Rate Limiting

Currently no rate limiting implemented. Consider adding for production.

---

## Authentication

Currently no authentication required (internal tool). Add before production deployment.

---

## CORS Configuration

Allowed origins (development):
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:5174`

Update `backend/app/main.py` for production URLs.

---

## Example Usage

### Python (requests)

```python
import requests

# Upload file
with open('file.xlsm', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8001/api/upload', files=files)
    data = response.json()
    print(f"Processed {data['data']['total_rows']} rows")

# Get rules
response = requests.get('http://localhost:8001/api/rules')
rules = response.json()
print(f"Found {len(rules)} rules")
```

### JavaScript (fetch)

```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8001/api/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(`Processed ${data.data.total_rows} rows`);
```

### cURL

```bash
# Upload file
curl -X POST http://localhost:8001/api/upload \
  -F "file=@path/to/file.xlsm"

# Get rules
curl http://localhost:8001/api/rules

# Create rule
curl -X POST http://localhost:8001/api/rules \
  -H "Content-Type: application/json" \
  -d '{"name": "New Rule", "priority": 5, "enabled": true, "config": {...}}'
```

---

## Testing APIs

Use the interactive Swagger UI at http://localhost:8001/docs to:
- View all endpoints
- See request/response schemas
- Test endpoints directly
- Download OpenAPI specification

---

For more information, see:
- [Developer Overview](developer-overview.md)
- [Database Schema](database-schema.md)
- [Setup Development](setup-development.md)
