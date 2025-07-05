# MCP Content Processor (MCP-Server)

A production-grade, platform-native, brand-aligned content engine for ideation, research, summarization, and content transformation.
**Optimized for Ethical AI Insider—scalable for multi-pillar, multi-platform, and workflow automation.**

---

## 📦 Repository Structure

mcp-server/
├── app/
│ ├── agents/
│ │ ├── headline.py
│ │ ├── compliance.py
│ │ └── formatter.py
│ ├── routes/
│ │ └── api.py
│ └── utils.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .dockerignore
└── README.md

---

## 🚀 Prerequisites

- Docker & Docker Compose installed
- OpenAI API key (`OPENAI_API_KEY`)
- (Optional) `MCP_SECRET` for secure API usage

---

## 🏗️ Building the Docker Image

```bash
docker build -t ghcr.io/mikeholownych/mcp:latest .
```

## 📦 Running with Docker Compose
```bash
docker-compose up -d
```
* Pass secrets at runtime via **.env** or **environment:** block.

## 📡 API Endpoints
### Health Check

- **GET /api/**
  - Returns **{ "status": "ok" }**

## Process Content

- **POST /api/process**
- Request JSON:
(all fields required unless marked optional)

```json
{
  "text": "Your idea or source content",
  "platform": "LinkedIn",      // or "Medium", "WordPress", "ConvertKit", etc.
  "pillar": "AI Risk",         // Content pillar (see below for suggestions)
  "name": "Draft Name",        // (optional) Internal draft title
  "brand": "Ethical AI Insider", // (optional) Defaults to this brand
  "context": "Additional context, notes, or audience hints" // (optional)
}
```
- Response JSON:

```json
{
  "safe": "...",                  // Brand-safe, compliance-checked draft
  "formatted": "...",             // Platform-optimized content (HTML, markdown, etc.)
  "headlines": ["...","...",...], // 5 headline/title options
  "platform": "LinkedIn",
  "pillar": "AI Risk",
  "brand": "Ethical AI Insider",
  "brandCompliance": "True: Content references key Ethical AI Insider themes.",
  "name": "Draft Name",
  "context": "..."
}
```

## Token Count
- **POST /api/tokens**
- Request JSON:

```json
{
  "text": "Your content here",
  "model": "gpt-4"
}
```
- Response JSON:
```json
{
  "tokens": 42,
  "model": "gpt-4"
}
```

## 🌐 Environment Variables
- OPENAI_API_KEY (required)
- MCP_SECRET (recommended for secure access)

See .env.example for format.

## 🏷️ Supported Content Pillars (Examples)
Update your automation and table to use these strategic pillars:
- AI Risk & Compliance
- Responsible AI Governance
- Operationalizing AI Ethics
- AI for Business Impact
- Leadership & Culture
- Emerging Trends & Regulation
- Practical Toolkits & Resources

## 🔗 Integration Example (n8n)
- Use an HTTP Request node to call **/api/process** and pass all required fields.
- Map MCP response fields to your Drafts table (Airtable, Notion, etc.) as documented above.

## 📝 License
MIT License.
© Mike Holownych
