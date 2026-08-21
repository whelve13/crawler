# Website Auditor

A production-quality asynchronous website crawler and SEO auditing platform.

## Architecture

This project consists of a FastAPI backend and a React frontend, backed by PostgreSQL. The crawler is built using `asyncio` and `httpx` for high performance, controlled concurrency, and robust error handling.

## Tech Stack

*   **Backend -** Python 3.12+, FastAPI, asyncio, httpx, BeautifulSoup4, SQLAlchemy 2.x, Alembic
*   **Database -** PostgreSQL
*   **Frontend -** React, TypeScript, Vite
*   **Infrastructure -** Docker, Docker Compose

## Installation & Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -e backend[dev]
```

## Running the Application

Using Docker Compose:

```bash
docker compose up
```

## Testing

Ensure your virtual environment is active, then navigate to the `backend/` directory and run:

```bash
cd backend
pytest
```
