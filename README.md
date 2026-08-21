# Website Auditor

A production-quality asynchronous website crawler and SEO auditing platform.

## Architecture

This project consists of a FastAPI backend and a React frontend, backed by PostgreSQL. 

### Deployment Architecture
- **Frontend**: The static React application is deployed on **GitHub Pages**.
- **Backend API**: The FastAPI application is deployed separately on a cloud provider (e.g. Render, Railway, AWS).
- **Database**: The PostgreSQL database must be accessible to the backend API.

```text
GitHub Pages
     │
     │ HTTPS
     ▼
Backend API
     │
     ▼
PostgreSQL
```

**Security & Configuration Details**:
- GitHub Pages hosts only the static frontend bundle.
- The `VITE_API_BASE` environment variable injected during the frontend build process points to the public Backend API URL.
- All application secrets (database credentials, private tokens) reside entirely backend-side and are NEVER exposed to the frontend.

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
