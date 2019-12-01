FROM python:3.7

RUN mkdir -p /app

ENV APP_HOME=/app
ENV PYTHONPATH=/app
ENV PORT=8080

WORKDIR /app/

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app ${APP_HOME}

EXPOSE ${PORT}

CMD exec uvicorn --host 0.0.0.0 --port ${PORT} main:app
