portfolio:
	curl -X POST -d '{"tickers": ["AA","AXP"], "endDate": "1993-01-01"}' localhost:8001/portfolio

server:
	docker-compose up

build:
	docker-compose build

push-to-local-registry:
	docker tag concord-fastapi_concord localhost:5001/concord-fastapi_concord:latest &&\
	docker tag concord-fastapi_backend localhost:5001/concord-fastapi_backend:latest &&\
	docker push localhost:5001/concord-fastapi_concord:latest &&\
	docker push localhost:5001/concord-fastapi_backend:latest

test-concord:
	cd concord && poetry run python -m pytest --pdb && cd ..

test-backend:
	cd backend && poetry run python -m pytest --pdb && cd ..

kind:
	./scripts/setup-local-cluster.sh &&\
	 ./scripts/push-images-to-local-registry.sh &&\
	 kubectl apply -f manifests/