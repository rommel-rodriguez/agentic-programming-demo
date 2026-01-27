# langgraph-demo

FastAPI backend that demonstrates an agentic workflow built with LangGraph and LangChain.
It exposes a single query endpoint and is intentionally minimal for experimentation.

## What this backend includes
- FastAPI app with lifespan-based logging setup.
- LangGraph agent that can call tools (Tavily search) and return a final response.
- Gemini model integration via `langchain-google-genai`.
- In-memory SQLite checkpointing for agent state.
- Skeleton domain + ORM mapping stubs for future expansion.

## API (current)
- `GET /query-lgmodel?query=...`
  - Runs the LangGraph agent and returns the model’s final answer.

## Configuration
Required environment variables (loaded via `pydantic-settings`):
- `gemini_api_key`
- `tavily_api_key`

## Run locally
From `langgraph-demo/`:
```
python -m uvicorn --app-dir src app.main:app --reload
```

## Notes
- This is a demo backend; several components are placeholders or partially implemented.
- The agent uses in-memory checkpointing, so state is not persisted across restarts.
