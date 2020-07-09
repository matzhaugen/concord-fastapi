build:
	docker build -t eu.gcr.io/experiment-ml-tk/hello-run .

run:
	
	cd app && docker run -it --rm -p 8000:80 -v $(pwd):/app eu.gcr.io/experiment-ml-tk/hello-run /start-reload.sh && cd ..

local:
	cd app && poetry run uvicorn main:app --reload && cd ..

request:
	curl -X POST -d '{"covariance": [[1,0,0],[0,1,0], [0, 0, 1]], "alpha":"0.1"}' localhost:8000/concord/

push: