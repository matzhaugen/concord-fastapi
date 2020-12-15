FROM openfaas/of-watchdog:0.7.2 as watchdog
FROM python:3.8-slim

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

RUN pip install --no-cache-dir uvicorn gunicorn starlette numpy pyconcord uvloop

COPY . /app
RUN addgroup --system app && adduser app --system --ingroup app
RUN chown app /app

USER app
WORKDIR /app

ENV fprocess="uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4"
ENV cgi_headers="true"
ENV mode="http"
ENV upstream_url="http://127.0.0.1:8000"

HEALTHCHECK --interval=5s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]