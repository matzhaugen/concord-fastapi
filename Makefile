build-concord:
	docker build -t eu.gcr.io/experiment-ml-tk/concord concord

run:
	cd concord && docker run -it --rm -p 8000:80 -v concord:/app eu.gcr.io/experiment-ml-tk/concord /start-reload.sh && cd ..

portfolio:
	curl -X POST -d '{"tickers": ["AA","AXP"], "endDate": "1993-01-01"}' localhost:8001/portfolio

server:
	docker-compose up

build:
	docker-compose build

test-concord:
	cd concord && poetry run python -m pytest --pdb && cd ..

test-backend:
	cd backend && poetry run python -m pytest --pdb && cd ..