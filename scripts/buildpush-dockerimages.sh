registry=${DOCKER_REGISTRY:-localhost:5001}
TAG=latest
DOCKER_BUILDKIT=1
# create registry container unless it already exists and local push is desired
if [ "${registry}" == 'localhost:5001' ]; then
	reg_name='kind-registry'
	reg_port='5001'
	running="$(docker inspect -f '{{.State.Running}}' "${reg_name}" 2>/dev/null || true)"
	if [ "${running}" != 'true' ]; then
	  docker run \
	    -d --restart=always -p "${reg_port}:5000" --name "${reg_name}" \
	    registry:2
	fi
fi
docker build -t ${registry}/concord-db:${TAG} -f concord/Dockerfile_db concord
docker build -t ${registry}/starlette-backend:${TAG} starlette-backend
docker build -t ${registry}/concord:${TAG} concord
docker push ${registry}/starlette-backend:${TAG}
docker push ${registry}/concord:${TAG}
docker push ${registry}/concord-db:${TAG}