registry=${DOCKER_REGISTRY:-localhost:5000}
DOCKER_BUILDKIT=1

# create registry container unless it already exists and local push is desired
if [ "${registry}" != 'localhost:5000' ]; then
	reg_name='kind-registry'
	reg_port='5000'
	running="$(docker inspect -f '{{.State.Running}}' "${reg_name}" 2>/dev/null || true)"
	if [ "${running}" != 'true' ]; then
	  docker run \
	    -d --restart=always -p "${reg_port}:5000" --name "${reg_name}" \
	    registry:2
	fi
fi

docker build -t ${registry}/starlette-backend:latest starlette-backend
docker build -t ${registry}/concord:latest concord
docker push ${registry}/starlette-backend:latest
docker push ${registry}/concord:latest