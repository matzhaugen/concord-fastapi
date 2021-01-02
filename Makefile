TAG=1
.PHONY: build

portfolio:
	curl -X POST -d '{"tickers": ["AA","AXP"], "endDate": "1993-01-01"}' localhost/portfolio-async

server:
	docker-compose down -v && docker-compose up --abort-on-container-exit --remove-orphans

down:
	docker-compose down -v
build:
	docker-compose build
of:
	faas up -f of-concord-fastapi.yml
ofow:
	echo $(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)
scale-of:
	kubectl scale deployment starlette-backend -n openfaas-fn --replicas=5 &&\
	kubectl scale deployment gateway -n openfaas --replicas=5

push-to-local-registry:
	DOCKER_REGISTRY=localhost:5002 ./scripts/buildpush-dockerimages.sh

test-concord:
	cd concord && poetry run python -m pytest --pdb && cd ..

test-backend:
	cd backend && poetry run python -m pytest --pdb && cd ..

do:
	kubectl create secret generic regcred \
    --from-file=.dockerconfigjson=${HOME}/.docker/config.json \
    --type=kubernetes.io/dockerconfigjson
	kubectl config use-context do-lon1-k8s-1-19-3-do-2-lon1-concord
	ENV=dev ./scripts/deploy-concord.sh
dev:
	ENV=dev; kubectl kustomize manifests/${ENV} > manifests/${ENV}/${ENV}.yaml && kubectl apply -f manifests/${ENV}/${ENV}.yaml
kind:
	./scripts/setup-local-cluster.sh &&\
	 ./scripts/push-images-to-local-registry.sh &&\
	 ENV=local ./scripts/deploy-concord.sh
frontend:
	cd frontend && npm i && npm start dev
registry:
	docker service create --name registry --publish published=5001,target=5000 registry:2
