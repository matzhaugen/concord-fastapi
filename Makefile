build-concord:
	docker build -t eu.gcr.io/experiment-ml-tk/concord app
run:
	cd app && docker run -it --rm -p 8000:80 -v app:/app eu.gcr.io/experiment-ml-tk/concord /start-reload.sh && cd ..

local:
	cd app && poetry run uvicorn main:app --reload && cd ..

request:
	curl -X POST -d '{"covariance": [[1,0,0],[0,1,0], [0, 0, 1]], "alpha":"0.1"}' localhost:8000/concord/

hey:
	hey -n 100 -m POST -d '{"covariance": [[1,0,0],[0,1,0], [0, 0, 1]], "alpha":"0.1"}' http://localhost:8000/concord/

push: