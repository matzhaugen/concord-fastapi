run:
	docker run -d -p 80:80 -v $(pwd):/app eu.gcr.io/experiment-ml-tk/hello-run /start-reload.sh

local:
	uvicorn app.main:app --reload
request:
	curl --request POST \
  --data '{"name":"xyz"}' \
	  http://localhost:8000/concord/ -H "Content-Type: application/json"