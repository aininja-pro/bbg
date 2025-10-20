# BBG Backend API

FastAPI-based REST API for processing rebate Excel files.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database and seed sample data:
```bash
# The database will be created automatically on first run
# To populate with sample data:
python seed_data.py
```

5. Start the development server:
```bash
uvicorn app.main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection & session
│   ├── models/              # SQLAlchemy models
│   │   ├── lookup.py       # Lookup table models
│   │   ├── rule.py         # Rules engine model
│   │   └── activity.py     # Activity log model
│   ├── schemas/             # Pydantic models
│   │   ├── lookup.py       # Lookup validation schemas
│   │   ├── rule.py         # Rule validation schemas
│   │   └── activity.py     # Activity log schemas
│   ├── repositories/        # Database access layer
│   │   └── lookup.py       # Lookup CRUD operations
│   ├── routers/             # API endpoints
│   │   └── lookup.py       # Lookup table endpoints
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── alembic/                 # Database migrations
├── tests/                   # Test files
├── seed_data.py            # Database seeding script
├── requirements.txt         # Python dependencies
└── README.md
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Available Endpoints

### Lookup Tables
- `GET /api/lookups/members` - List all TradeNet members
- `POST /api/lookups/members` - Create a new member
- `GET /api/lookups/members/{id}` - Get member by ID
- `PUT /api/lookups/members/{id}` - Update a member
- `DELETE /api/lookups/members/{id}` - Delete a member
- `DELETE /api/lookups/members` - Delete all members

Similar endpoints exist for `/suppliers` and `/products`.

## Seeding Sample Data

To populate the database with sample data for testing:

```bash
python seed_data.py
```

This will create:
- 5 sample TradeNet Members
- 5 sample Suppliers
- 7 sample Programs & Products

## Testing

```bash
pytest
```

## Database Migrations

Using Alembic for database version control:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```
