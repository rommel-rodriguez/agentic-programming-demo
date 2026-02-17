# langgraph-demo

Agentic workflow backend built with FastAPI, LangGraph, and LangChain.

## Why this project is strong
- Implements a real tool-calling graph workflow (LLM -> tool -> LLM loop), not a single prompt wrapper.
- Supports thread-aware state via LangGraph checkpointing, so conversations can continue by `thread_id`.
- Uses a layered architecture (`entrypoints`, `ports`, `adapters`, `services`, `domain`) for maintainability.
- Includes structured JSON logs and correlation IDs for observability.
- Runs in Docker with a Postgres-backed checkpointer for realistic local development.

## Tech stack
- Python 3.11
- FastAPI + Uvicorn
- LangGraph + LangChain
- Gemini (`langchain-google-genai`)
- Tavily tool integration (`langchain-tavily`)
- Postgres (`psycopg`, `psycopg_pool`)

## Current API
### Agent workflow
- `GET /wf/query-lgmodel?query=...&thread_id=...`
  - Runs the LangGraph agent and returns the final answer.

### Invoice workflow (scaffold)
- `POST /invoice/attachments/init`
- `PUT /invoice/attachments/{id}/content`
- `POST /invoice/runs`

## Run with Docker Compose (recommended)
From repo root:
```bash
docker compose up --build
```

Required `.env` values in repo root:
```env
gemini_api_key=YOUR_GEMINI_API_KEY
tavily_api_key=YOUR_TAVILY_API_KEY
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app
```

Open docs at:
```text
http://localhost:8000/docs
```

## Run locally (without Docker)
From `langgraph-demo/`:
```bash
python -m uvicorn --app-dir src app.entrypoints.webapp.asgi:app --reload
```

Note: default app startup expects a valid `DB_URL` for Postgres checkpointing.

## What this demonstrates to employers
- Agentic backend design with explicit workflow orchestration.
- Practical LLM integration with external tool usage.
- Service decomposition with clear boundaries and dependency injection through FastAPI dependencies.
- Production-aware backend practices: structured logging, request correlation, containerized execution.

## Scope notes
- This project is actively evolving.
- Some modules (especially invoice pipeline and service layer pieces) are scaffolded for next iterations.
- Test structure exists, but test coverage is still limited.

## Authors
- Rommel Rodriguez Perez - rommelrodperez@gmail.com
