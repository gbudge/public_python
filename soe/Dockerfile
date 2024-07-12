FROM python:3

ARG APP_USER=appuser
RUN useradd -m ${APP_USER}
USER ${APP_USER}

RUN pip install --upgrade pip