# All the lg-prefixed targets are for the langgraph-demo backend
.PHONY: lg-schema-check
lg-schema-check:
	docker compose --profile dev up psdb