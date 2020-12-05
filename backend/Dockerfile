FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

RUN apt update && apt install -y curl &&\
 	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false &&\
    apt remove -y curl && apt -y autoremove


# # Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./app/poetry.lock* /app/

RUN poetry install --no-root --no-dev
WORKDIR /app/
COPY ./src/ /app/src/