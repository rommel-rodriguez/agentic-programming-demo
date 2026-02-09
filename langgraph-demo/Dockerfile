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

RUN python3 -m pip install --upgrade pip 

WORKDIR /app

RUN addgroup --gid ${USER_GID} ${USERNAME} && \
    adduser --uid $USER_UID --gid ${USER_GID} ${USERNAME}

COPY --chown=root:root . ./

# Install dependencies; include test/dev extras only when APP_ENV=test.
RUN if [ "$APP_ENV" = "test" ]; then \
      pip install -e . --group dev --group test; \
    else \
      pip install .; \
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


USER ${USERNAME} 

CMD [ "uvicorn","--host", "0.0.0.0","--app-dir", "src", "app.entrypoints.webapp.asgi:app" ]
