FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application code and requirements
COPY ./app /app/app
COPY requirements.txt /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose port for FastAPI/Uvicorn
EXPOSE 5005

# Healthcheck for container
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:5005/ || exit 1

# Set environment variables for unbuffered logging (better for Docker)
ENV PYTHONUNBUFFERED=1

# Entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5005"]
