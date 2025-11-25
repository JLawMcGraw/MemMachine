FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
RUN pip install uv

# Copy requirements
COPY requirements.txt* pyproject.toml* ./

# Install Python dependencies
RUN if [ -f requirements.txt ]; then uv pip install --system -r requirements.txt; fi
RUN if [ -f pyproject.toml ]; then uv pip install --system -e .; fi

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=15s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run bar server
CMD ["python", "bar_server.py"]
