FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy application code and requirements
COPY ./app /app/app
COPY requirements.txt /app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose port for FastAPI/Uvicorn
EXPOSE 5005

# (Optional) Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:5005/ || exit 1

# Entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5005"]
