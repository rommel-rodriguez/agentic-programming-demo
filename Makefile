# All the lg-prefixed targets are for the langgraph-demo backend
.PHONY: lg-check
lg-check:
	docker compose --profile dev run  --rm app alembic check
