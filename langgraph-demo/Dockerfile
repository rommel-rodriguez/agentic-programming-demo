FROM python:3.11-bookworm

ARG USER_UID=1001
ARG USER_GID=1001
ARG USERNAME=appuser
ARG APP_ENV=prod

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /var/cache/apt/archives/*.deb

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install uv

WORKDIR /app

RUN addgroup --gid ${USER_GID} ${USERNAME} && \
    adduser --uid $USER_UID --gid ${USER_GID} ${USERNAME}

COPY --chown=root:root . ./

# Install dependencies with uv. When present, BuildKit secrets allow uv to
# authenticate to the GitLab package index without persisting credentials in
# image layers or environment metadata.
RUN --mount=type=secret,id=gitlab_user \
    --mount=type=secret,id=gitlab_password \
    if [ -f /run/secrets/gitlab_user ]; then \
      export UV_INDEX_GITLAB_USERNAME="$(cat /run/secrets/gitlab_user)"; \
    fi && \
    if [ -f /run/secrets/gitlab_password ]; then \
      export UV_INDEX_GITLAB_PASSWORD="$(cat /run/secrets/gitlab_password)"; \
    fi && \
    if [ "$APP_ENV" = "test" ]; then \
      uv sync --frozen --group dev --group test; \
    else \
      uv sync --frozen --no-dev; \
    fi

# Remove tests from production images, then harden /app as read-only.
RUN if [ "$APP_ENV" != "test" ]; then rm -rf /app/tests; fi \
 && chmod -R a=rX /app/ \
 && chmod -R a-w  /app/ \
 && mkdir -p /var/lib/app /tmp/app \
 && chown -R ${USERNAME}:${USERNAME} /var/lib/app /tmp/app \
 && chmod 700 /var/lib/app /tmp/app

# Avoid __pycache__ in /app and force pytest cache into writable /tmp/app.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTEST_CACHE_DIR=/tmp/app/pytest_cache
ENV PATH="/app/.venv/bin:${PATH}"


USER ${USERNAME} 

CMD [ "uvicorn","--host", "0.0.0.0","--app-dir", "src", "app.entrypoints.webapp.asgi:app" ]
