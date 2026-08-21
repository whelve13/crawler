FROM python:3.12-slim

WORKDIR /app

# Install build dependencies for some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install uv

# Copy only the files needed for dependency installation
COPY pyproject.toml README.md ./

# Install dependencies via uv
RUN uv pip install --system -e .[dev]

# Copy application code
COPY ./app /app/app
COPY ./tests /app/tests

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
