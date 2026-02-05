FROM python:3.11-bookworm

ARG USER_UID=1001
ARG USER_GID=1001
ARG USERNAME=appuser

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

COPY --chown=root:root ./pyproject.toml ./README.md ./ 

# Make code readable + traversable, but not writable by anyone.
# - a=rX  : everyone gets read; directories (and already-exec files) get execute
# - a-w   : remove write from user/group/other (including root as "owner" per mode bits)
RUN chmod -R a=rX /app/ \
 && chmod -R a-w  /app/
# -----------------------------
# 3) Create runtime-writable directories (keep them OUT of /app/src)
# -----------------------------
RUN mkdir -p /var/lib/app /tmp/app \
 && chown -R ${USERNAME}:${USERNAME} /var/lib/app /tmp/app \
 && chmod 700 /var/lib/app /tmp/app


# TODO: Modify this later so that the dev and test depencies are not installed for the
# production build.
RUN pip install . && pip install --group dev --group test


COPY --chown=root:root . ./ 


USER ${USERNAME} 

CMD [ "uvicorn","--host", "0.0.0.0","--app-dir", "src", "app.entrypoints.webapp.asgi:app" ]