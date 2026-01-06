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

COPY --chown=appuser:appgroup  ./pyproject.toml ./README.md ./ 

RUN pip install . && pip install --group dev --group test

COPY --chown=appuser:appgroup  . ./ 

USER ${USERNAME} 

CMD [ "uvicorn", "--reload","--host", "0.0.0.0","--app-dir", "src", "app.main:app" ]