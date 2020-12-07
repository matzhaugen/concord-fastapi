portfolio:
	curl -X POST -d '{"tickers": ["AA","AXP"], "endDate": "1993-01-01"}' localhost/portfolio

server:
	docker-compose up

down:
	docker-compose down -v
build:
	docker-compose build

push-to-local-registry:
	docker tag concord-fastapi_concord localhost:5000/concord-fastapi_concord:latest &&\
	docker tag concord-fastapi_backend localhost:5000/concord-fastapi_backend:latest &&\
	docker push localhost:5000/concord-fastapi_concord:latest &&\
	docker push localhost:5000/concord-fastapi_backend:latest

test-concord:
	cd concord && poetry run python -m pytest --pdb && cd ..

test-backend:
	cd backend && poetry run python -m pytest --pdb && cd ..

kind:
	./scripts/setup-local-cluster.sh &&\
	 ./scripts/push-images-to-local-registry.sh &&\
	 kubectl apply -f manifests/