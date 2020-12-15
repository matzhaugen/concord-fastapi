registry=${DOCKER_REGISTRY:-localhost:5000}
DOCKER_BUILDKIT=1
docker build -t ${registry}/starlette-backend:latest starlette-backend
docker build -t ${registry}/concord:latest concord
docker push ${registry}/starlette-backend:latest
docker push ${registry}/concord:latest