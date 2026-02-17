# FAPI01 - Backend Portfolio

Primary backend project: **`langgraph-demo`** (agentic workflow microservice).

## Flagship project: `langgraph-demo`
`langgraph-demo` is a FastAPI microservice that implements agentic workflows using LangGraph + LangChain, with tool-calling, thread-aware state, and Postgres-backed checkpointing.

## Why this backend is portfolio-relevant
- Real workflow graph orchestration (LLM/tool loop), not just a chat wrapper.
- Stateful execution model using `thread_id` and LangGraph checkpoints.
- Clean architecture direction with `ports`, `adapters`, `services`, and web `entrypoints`.
- Structured JSON logs with correlation IDs for request tracing.
- Dockerized local environment with Postgres and healthchecks.

## Stack
- Python 3.11
- FastAPI / Uvicorn
- LangGraph / LangChain
- Gemini + Tavily tool integration
- Postgres + psycopg
- Pydantic Settings
- Ruff + MyPy configuration

## Quickstart
1. Create `.env` in repo root:
```env
gemini_api_key=YOUR_GEMINI_API_KEY
tavily_api_key=YOUR_TAVILY_API_KEY
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app
```

2. Start the stack:
```bash
docker compose up --build
```

3. Open API docs:
```text
http://localhost:8000/docs
```

## Current API surface (`langgraph-demo`)
- `GET /wf/query-lgmodel?query=...&thread_id=...`
- `POST /invoice/attachments/init` (scaffold)
- `PUT /invoice/attachments/{id}/content` (scaffold)
- `POST /invoice/runs` (scaffold)

## Repository layout
```text
.
├─ langgraph-demo/    # Main backend project (agentic workflow microservice)
├─ be1/               # Secondary upload-streaming playground
├─ infra/             # Infrastructure workspace (placeholder)
└─ docker-compose.yml # Local dev stack for langgraph-demo + Postgres
```

## Current maturity
- `langgraph-demo` is the main project and active focus.
- Some modules are intentionally scaffolded and being expanded iteratively.
- The repository is designed to show architecture, agentic orchestration, and integration patterns.

## Authors
- Rommel Rodriguez Perez - rommelrodperez@gmail.com
