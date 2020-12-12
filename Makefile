TAG=1
.PHONY: build
portfolio:
	curl -X POST -d '{"tickers": ["AA","AXP"], "endDate": "1993-01-01"}' localhost/portfolio

server:
	docker-compose down -v && docker-compose up --abort-on-container-exit

down:
	docker-compose down -v
build:
	docker-compose build
of:
	faas up -f of-concord.yml
ofow:
	echo $(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)

push-to-local-registry:
	docker tag concord-fastapi_concord localhost:5000/concord-fastapi_concord:${TAG} &&\
	docker tag concord-fastapi_backend localhost:5000/concord-fastapi_backend:${TAG} &&\
	docker push localhost:5000/concord-fastapi_concord:${TAG} &&\
	docker push localhost:5000/concord-fastapi_backend:${TAG}

test-concord:
	cd concord && poetry run python -m pytest --pdb && cd ..

test-backend:
	cd backend && poetry run python -m pytest --pdb && cd ..

kind:
	./scripts/setup-local-cluster.sh &&\
	 ./scripts/push-images-to-local-registry.sh &&\
	 ./setup-openfaas.sh &&\
	 kubectl apply -f manifests/concord.yaml
