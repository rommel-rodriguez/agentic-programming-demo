# All the lg-prefixed targets are for the langgraph-demo backend
.PHONY: lg-check lg-up lg-down lg-revision

M = "default create-revision message"

lg-up:
	docker compose --profile dev up lg-app psdb
lg-down:
	docker compose --profile dev down lg-app psdb --remove-orphans
lg-check:
	docker compose --profile dev run \
		--rm lg-app alembic check
lg-revision:
	docker compose --profile dev run \
		--rm lg-app alembic revision --autogenerate -m "$(M)"
lg-upgrade-db:
	docker compose --profile dev run \
		--rm lg-app alembic upgrade head 
