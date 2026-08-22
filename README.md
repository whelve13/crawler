<h1 align="center">
  <br>
  Website Auditor & Crawler
  <br>
</h1>

<h4 align="center">An asynchronous web crawler and SEO auditing platform that analyzes website structure, links, HTTP health, and SEO metadata through an interactive reporting dashboard.</h4>

<p align="center">
  <a href="#live-demo">Live Demo</a> •
  <a href="#key-features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#how-it-works">How To Use</a> •
  <a href="#security">Security</a>
</p>

---

## Live Demo

The project is currently deployed and accessible live:

- **Frontend UI (GitHub Pages):** [https://whelve13.github.io/crawler/](https://whelve13.github.io/crawler/)
- **Backend API (Render):** [https://crawler-api-ghwd.onrender.com](https://crawler-api-ghwd.onrender.com)

> **Note:** The backend uses a free tier on Render which spins down after 15 minutes of inactivity. It may take up to 50 seconds for the initial API request to wake the server up.

## Key Features

### 🕸️ Crawling & Discovery
- **Asynchronous Engine:** High-performance, highly concurrent crawling powered by Python's syncio and httpx.
- **Configurable Limits:** Users can enforce strict depth constraints and maximum page bounds to constrain crawl scope.
- **Link Discovery:** Automatically parses HTML to discover, normalize, and enqueue internal links.
- **Health Tracking:** Records HTTP status codes, tracks redirection chains/loops, and surfaces broken links.

### 📈 SEO Analysis
- **Metadata Extraction:** Extracts and analyzes Title tags, Meta Descriptions, and Canonical URLs.
- **Content Hierarchy:** Parses <h1>, <h2>, and <h3> tags to evaluate semantic structure.
- **Automated Rule Evaluation:** Flags common SEO problems (e.g., missing titles, descriptions too short/long, missing H1s).

### 📊 Interactive Reporting
- **Data Visualizations:** Built-in charting for HTTP status distribution across the crawled domain.
- **Tabular Data:** Searchable, filterable list of all crawled URLs, status codes, and specific SEO issues discovered on each page.
- **Performance Metrics:** Reports total duration, pages crawled per second, and failed network requests.

### 🗺️ Site Architecture Graph
- **Directed Force Graph:** An interactive 2D node-graph visualization of the website's internal linking structure.
- **Orphan Detection:** Visually identifies pages that lack incoming internal links.
- **Status Indicators:** Color-codes nodes to instantly spot HTTP 4xx/5xx errors or significant SEO warnings across the architecture.

## Architecture

`mermaid
flowchart LR
    Client([Browser / User]) -->|HTTPS| UI[React SPA<br>GitHub Pages]
    UI -->|REST API| API[FastAPI Backend<br>Render]
    
    subgraph Backend Infrastructure
        API -->|Task Enqueue| Worker[Background Tasks]
        Worker <--> Engine[Crawler Engine]
        Engine <--> Internet((Target<br>Website))
        
        API <--> DB[(PostgreSQL)]
        Worker -->|Persist Results| DB
    end
`

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React, TypeScript, Vite | Core UI framework and bundler |
| **Styling** | Tailwind CSS | Utility-first styling (Amber CRT Retro Theme) |
| **Visualizations** | Recharts, react-force-graph-2d | Charting and site architecture mapping |
| **Backend** | Python 3.12, FastAPI | High-performance asynchronous REST API |
| **Crawler** | httpx, BeautifulSoup4 | Async network requests and HTML parsing |
| **Database** | PostgreSQL, SQLAlchemy, asyncpg | Relational data persistence and ORM |
| **Migrations** | Alembic | Database schema versioning |
| **Testing** | pytest, itest | Automated unit and integration testing |
| **CI/CD** | GitHub Actions | Automated linting (Ruff), testing, and deployment |
| **Hosting** | Render, GitHub Pages | Containerized backend and static frontend hosting |

## How It Works

1. **Submission:** The user submits a target URL, max depth, and max pages via the Dashboard.
2. **Validation:** The backend validates the request payload and applies strict SSRF checks against the target hostname.
3. **Queueing:** The API returns a 	ask_id immediately and spins up a background worker.
4. **Crawling:** The CrawlerEngine manages an asynchronous queue, fetching URLs concurrently without exceeding the designated connection pool limits.
5. **Parsing & Auditing:** Successful HTML responses are parsed to extract metadata, headers, and internal links. The SEO engine audits the extracted data.
6. **Persistence:** Crawl metrics, page states, and specific SEO/Health issues are bulk-committed to PostgreSQL.
7. **Rendering:** The React frontend polls for task completion and retrieves the serialized JSON report to render interactive charts, tables, and force-directed graphs.

## Security

This repository implements multiple defensive mechanisms to protect the host infrastructure and the public API from abuse:

- **Server-Side Request Forgery (SSRF) Protection:** The is_safe_url utility intercepts all outgoing crawl requests. It performs a DNS resolution and rejects any URL that resolves to a private, loopback, link-local, multicast, or reserved IP address (IPv4 and IPv6). This prevents attackers from crawling the internal network or AWS metadata endpoints.
- **Resource Exhaustion Limits:** 
  - MAX_FILE_SIZE_BYTES prevents the crawler from downloading massive files (e.g., ISOs, videos) by checking the Content-Length header upfront and aborting the HTTP stream if the limit is exceeded.
  - Strict upper bounds on max_pages and max_depth are enforced via Pydantic schema validation.
- **Rate Limiting:** IP-based rate limiting is enforced via slowapi to prevent API spam (e.g., max 5 crawl requests per minute).
- **Concurrency Capping:** A global thread-safe CrawlConcurrencyManager rejects new crawl submissions with a 503 Service Unavailable if the server is currently processing its maximum allowed number of concurrent crawls.
- **Environment Secrets:** No sensitive credentials or API keys are exposed in the frontend or version control.

> **Note on SSRF TOCTOU:** While the SSRF protection performs upfront DNS resolution and IP validation, a highly sophisticated DNS Rebinding attack (TOCTOU) could theoretically bypass it since the httpx client performs a secondary DNS resolution. Hardening against DNS rebinding would require a custom DNS resolver patched directly into httpx.

## Project Structure

`	ext
crawler/
├── .github/workflows/          # CI/CD pipelines (Lint, Test, Deploy)
├── backend/
│   ├── alembic/                # Database migrations
│   ├── app/
│   │   ├── api/endpoints/      # FastAPI route controllers
│   │   ├── core/               # App config, rate limits, concurrency
│   │   ├── crawler/            # Core engine, HTTP client, parsing, SSRF rules
│   │   ├── db/                 # Asyncpg session and base models
│   │   ├── models/             # SQLAlchemy ORM models (Task, Page, SEOIssue)
│   │   └── schemas/            # Pydantic validation models
│   ├── tests/                  # Pytest suite
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable React components (CrawlForm, SiteGraph)
│   │   ├── pages/              # Dashboard and CrawlReport views
│   │   └── services/           # API client wrappers
│   ├── tests/                  # Vitest suite
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml          # Local full-stack orchestration
`

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/crawl/ | Initializes a new crawl task. Requires start_url. Optional: max_pages, max_depth. Returns a 	ask_id. |
| GET | /api/v1/crawl/ | Returns a list of recently dispatched crawl tasks and their current lifecycle statuses. |
| GET | /api/v1/crawl/{task_id} | Retrieves the real-time execution status and metrics for a specific task. |
| GET | /api/v1/crawl/{task_id}/report | Fetches the comprehensive, serialized crawl report including all pages, SEO issues, and health warnings. |

## Local Development

The easiest way to run the entire stack locally is by using Docker Compose.

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Start the Stack

Clone the repository and run Docker Compose from the root directory:

`ash
git clone https://github.com/whelve13/crawler.git
cd crawler

# This will build the frontend/backend images and start PostgreSQL
docker-compose up --build
`

### 2. Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation (Swagger UI):** http://localhost:8000/docs

The docker-compose.yml is configured to automatically run database migrations (lembic upgrade head) before starting the backend API.

## Environment Variables

For manual deployment or non-Docker local setups, the backend requires a .env file in the ackend/ directory:

`nv
# Example backend/.env
ENVIRONMENT=development
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=crawler
# Alternatively, provide a full connection string:
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/crawler

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
`

The frontend requires environment variables configured at build-time (in .env or injected via CI):

`nv
# Example frontend/.env
VITE_API_BASE=http://localhost:8000/api/v1
`

## License

This project is licensed under the MIT License.
