# Crawler

A production-quality asynchronous website crawler and SEO auditing platform.

## Architecture

This project consists of a FastAPI backend and a React frontend, backed by PostgreSQL. 

## Environments & CI/CD Pipeline

This project makes a clear distinction between development, integration, and production environments to keep the local development experience simple and accessible.

### 1. Local Development
- **No Docker or PostgreSQL required locally.** You can develop the frontend using Vite (`npm run dev`) and run the backend tests that mock database behavior.
- **Run local tests:** 
  - Frontend: `npm run test`
  - Backend (pure logic): `pytest tests/` (Database integration tests will safely fail or be skipped if PostgreSQL is not running).
- **Run local quality checks:** 
  - Frontend: `npm run lint` and `npx tsc --noEmit`
  - Backend: `ruff check backend/`

### 2. CI Integration Environment (Automated Quality Gates)
- **GitHub Actions** runs automatically on every Push and Pull Request.
- **What CI checks:**
  - **Backend**: Runs Ruff linting and the complete `pytest` test suite.
  - **PostgreSQL Integration**: CI automatically spins up a `postgres:15` service container, runs Alembic migrations, and verifies API/Database integration tests (`test_api_crawl.py`).
  - **Frontend**: Runs Vitest, `oxlint`, `tsc` type checking, and verifies a complete production build (`npm run build`).
  - **Security**: Ensures no `.env` files or secrets are accidentally committed.
- **Full integration testing occurs exclusively in CI.**

### 3. Production Environment
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
