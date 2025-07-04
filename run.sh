#!/usr/bin/env bash
# Entrypoint for local development

# Load environment variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
elif [ -f .env.example ]; then
  echo "Using .env.example—please copy to .env and fill in secrets."
  export $(grep -v '^#' .env.example | xargs)
fi

# Start the FastAPI server with live reload
uvicorn app.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 5005
