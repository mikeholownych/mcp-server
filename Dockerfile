# Dockerfile to containerize the FastAPI application
FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn pydantic

CMD ["uvicorn", "mcp_server.enhancement_approval:app", "--host", "0.0.0.0", "--port", "80"]