FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2 and building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY ./backend/pyproject.toml ./backend/README.md ./

# Install dependencies
RUN pip install --no-cache-dir .

# Copy application code
COPY ./backend /app/

# Expose port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
