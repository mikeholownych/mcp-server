# MCP Content Processor (MCP-Server)

A production-grade multimodal content processor for ideation, research, summarization, and content transformation.

## 📦 Repository Structure

```
mcp-server/
├── app/
│   ├── agents/
│   │   ├── headline.py
│   │   ├── compliance.py
│   │   └── formatter.py
│   ├── routes/
│   │   └── api.py
│   └── utils.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .dockerignore
└── README.md
```

## 🚀 Prerequisites

- Docker & Docker Compose installed
- OpenAI API key

## 🏗️ Building the Docker Image

```bash
docker build -t ghcr.io/mikeholownych/mcp:latest .
```

## 📦 Running with Docker Compose

```bash
docker-compose up -d
```

## 📡 API Endpoints

- **Health Check**  
  `GET /`  
  Returns `{ "status": "ok" }`

- **Process Content**  
  `POST /api/process`  
  Request JSON:
  ```json
  {
    "text": "Your content here",
    "platform": "LinkedIn"  // or "ConvertKit", "Medium", etc.
  }
  ```
  Response JSON:
  ```json
  {
    "formatted": "...",
    "safe": "...",
    "headlines": ["...","...",...]
  }
  ```

- **Token Count**  
  `POST /api/tokens`  
  Request JSON:
  ```json
  {
    "text": "Your content here",
    "model": "gpt-4"
  }
  ```
  Response JSON:
  ```json
  {
    "tokens": 42,
    "model": "gpt-4"
  }
  ```

## 🌐 Environment Variables

See `.env.example` for required variables.

## 📝 License

MIT License. © Mike Holownych
