# FAPI01 - Agentic FastAPI + LangGraph Demo

![python](https://img.shields.io/badge/python-3.11-blue)
![fastapi](https://img.shields.io/badge/FastAPI-0.121-009688)
![langgraph](https://img.shields.io/badge/LangGraph-enabled-5c7cfa)
![langchain](https://img.shields.io/badge/LangChain-enabled-2f9e44)
![docker](https://img.shields.io/badge/Docker-ready-2496ED)

Demo project showcasing agentic programming patterns with FastAPI and LangChain/LangGraph.
This is intentionally incomplete and focused on learning and experimentation, not production.

## Status
- Work in progress: some modules are placeholders or partial implementations.
- Expect missing pieces (tests, persistence wiring, error handling, auth, etc.).

## Highlights
- FastAPI endpoints for streaming file uploads (PDF and binary examples).
- LangGraph-based agent that can call tools (Tavily search) with a Gemini model.
- In-memory checkpointing via SQLite for agent state.
- Pydantic Settings for configuration.
- DDD / clean-architecture inspired layout with adapters, domain, and entrypoints.
- Docker-based dev workflow with auto-reload.

## Project layout
```
.
├─ be1/               # FastAPI upload streaming playground
├─ langgraph-demo/    # LangGraph + FastAPI demo app
├─ infra/             # Placeholder (k8s dir currently empty)
└─ docker-compose.yml # Runs langgraph-demo
```

## Quickstart (Docker Compose)
1) Create an `.env` file in the repo root:
```
gemini_api_key=YOUR_GEMINI_API_KEY
tavily_api_key=YOUR_TAVILY_API_KEY
```

2) Build and run:
```
docker compose up --build
```

3) Open the API docs:
```
http://localhost:8000/docs
```

## API surface (current)
### langgraph-demo
- `GET /query-lgmodel?query=...`
  - Runs a LangGraph agent with a Tavily search tool and returns the final response.

### be1 (run separately)
- `POST /upload/pdf-streaming` - stream a PDF upload to disk.
- `POST /upload/binary-streaming` - stream any binary file with optional size limit.
- `POST /upload/pdf-small` - read a small PDF fully into memory and save.
- `GET /test-string`
- `GET /test-dict`

## Running be1 locally
From `be1/`:
```
python -m uvicorn --app-dir src app.main:app --reload
```

## Notes and limitations
- The LangGraph agent is configured for Gemini + Tavily; valid API keys are required.
- Persistence and domain models are skeletal and intended for iteration.
- This repo is a demo, so the structure may evolve as experiments continue.

## Authors
- Rommel Rodriguez Perez - rommelrodperez@gmail.com

## Tags
`#fastapi` `#langchain` `#langgraph` `#agentic` `#python` `#docker` `#pydantic`
`#sqlalchemy` `#ddd` `#clean-architecture` `#uvicorn`
