# Equipment Monitoring & Alert Platform

A small REST service for tracking equipment state, telemetry, and operational alerts.

## Stack
Python, FastAPI, SQLite, SQLAlchemy, Pydantic, Pytest

## Run
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open `/docs` for the interactive API.

## Core behavior
- Register and update equipment records.
- Validate status and temperature boundaries.
- Filter equipment by operational status.
- Surface degraded and unavailable equipment through `/alerts`.
- Automated tests cover health, validation, CRUD, and alert behavior.
