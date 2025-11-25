# Alchemix Bar Assistant - MemMachine Integration

This directory contains the Alchemix Bar Assistant agent, which provides AI memory capabilities for the Alchemix cocktail app.

## Architecture

The Bar Assistant consists of:
- **BarQueryConstructor**: Enriches user queries with semantic keywords
- **bar_server.py**: FastAPI server that exposes the memory API
- **ingest_recipes.py**: Script to populate the knowledge base with recipes
- **MemMachine Backend**: Core memory service (runs separately)

## Prerequisites

1. **Python 3.12+** with `uv` package manager
2. **Neo4j Database** (for vector storage)
3. **Postgres Database** (for profile storage used by memmachine-server)
4. **OpenAI API Key** (for embeddings)
5. **Alchemix Backend** (for recipe ingestion)

## Setup Instructions

### 1. Install Dependencies

From the `memmachine` root directory:

```bash
cd /path/to/memmachine
uv sync
```

### 2. Start Neo4j Database

**Option A: Docker (Recommended)**
```bash
docker run \
    --name neo4j-alchemix \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/your_password_here \
    -d neo4j:latest
```

**Option B: Local Installation**
Download from https://neo4j.com/download/ and follow installation instructions.

### 3. Configure Environment Variables

Copy the example env file and fill in your API keys:

```bash
cd examples/bar_assistant
cp .env.example .env
```

Edit `.env` and set:
- `OPENAI_API_KEY` - Your OpenAI API key
- `NEO4J_PASSWORD` - Your Neo4j password
- `POSTGRES_PASSWORD` - Your Postgres password (host/user/db/port default to localhost/postgres/postgres/5432)
- `ALCHEMIX_JWT_TOKEN` - JWT token from Alchemix (for ingestion only)

### 4. Start MemMachine Backend

From the memmachine root directory:

```bash
uv run memmachine-server --config examples/bar_assistant/config.yaml
```

This starts the core memory service on `http://localhost:8080`.

### 5. Start Bar Assistant Server

In a new terminal:

```bash
cd examples/bar_assistant
uv run python bar_server.py
```

This starts the bar assistant API on `http://localhost:8001`.

### 6. Ingest Recipes (One-Time Setup)

Make sure the Alchemix backend is running, then:

```bash
# Get a JWT token from Alchemix UI (DevTools > Local Storage > token)
export ALCHEMIX_JWT_TOKEN="your_token_here"

# Run the ingestion script
uv run python ingest_recipes.py
```

## API Endpoints

### POST /memory
Store a new memory

```bash
curl -X POST http://localhost:8001/memory \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "query": "I love spicy margaritas"
  }'
```

### GET /memory
Retrieve relevant memories

```bash
curl "http://localhost:8001/memory?user_id=user123&query=suggest%20a%20drink"
```

## Testing

```bash
# Test the query constructor
uv run python -m pytest examples/bar_assistant/test_query_constructor.py

# Test the API endpoints
curl http://localhost:8001/memory?user_id=test&query=hello
```

## Troubleshooting

**Neo4j Connection Failed:**
- Check Neo4j is running: `docker ps` or check Neo4j Desktop
- Verify password in `.env` matches Neo4j password
- Check bolt URL: `bolt://localhost:7687`

**OpenAI API Errors:**
- Verify API key is valid
- Check you have credits: https://platform.openai.com/usage

**Recipe Ingestion Fails:**
- Ensure Alchemix backend is running on `http://localhost:3000`
- Check JWT token is valid (tokens expire after 24 hours)
- Verify `ALCHEMIX_API_URL` in `.env`

## Next Steps

Once the Bar Assistant is running:
1. Integrate with Alchemix backend (Phase 5)
2. Update Alchemix chat routes to use MemoryService
3. Test end-to-end RAG pipeline
4. Deploy to production
