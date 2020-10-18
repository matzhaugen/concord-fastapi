build-concord:
	docker build -t eu.gcr.io/experiment-ml-tk/concord concord
run:
	cd concord && docker run -it --rm -p 8000:80 -v concord:/app eu.gcr.io/experiment-ml-tk/concord /start-reload.sh && cd ..

local:
	cd concord && poetry run uvicorn main:app --reload && cd ..

request:
	curl -X POST -d '{"covariance": [[1,0,0],[0,1,0], [0, 0, 1]], "alpha":"0.1"}' localhost:8000/concord/

hey:
	hey -n 100 -m POST -d '{"covariance": [[1,0,0],[0,1,0], [0, 0, 1]], "alpha":"0.1"}' http://localhost:8000/concord/

server:
	docker-compose up

middleware:
	docker build -t matzhaugen/middleware:latest middleware

test-middleware:
	cd middleware/src && poetry run python -m pytest --pdb && cd ../..

smoke: 
	curl -X POST localhost:8001/portfolio/ -d '{"tickers": ["AA", "AXP"], "method": "concord"}'