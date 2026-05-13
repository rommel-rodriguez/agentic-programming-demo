FROM python:3.11-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY . /app

RUN pip install .

RUN mkdir -p /var/lib/auth/keys /var/lib/auth/data

ENV AUTH_KEYS_DIR=/var/lib/auth/keys
ENV AUTH_DB_URL_SQLALCHEMY=sqlite+aiosqlite:////var/lib/auth/data/auth.db

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src", "app.entrypoints.webapp.asgi:app"]
