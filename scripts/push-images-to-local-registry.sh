# Read manifests and extract all images
images=$(perl -ne 'print "$1\n" if /image: (.*)/' manifests/concord.yaml)
images+=" "
required_images=($images)

docker tag concord-fastapi_concord localhost:5000/concord-fastapi_concord:latest &&\
docker tag concord-fastapi_backend localhost:5000/concord-fastapi_backend:latest &&\
docker push localhost:5000/concord-fastapi_concord:latest &&\
docker push localhost:5000/concord-fastapi_backend:latest

# Pull the required images and push them to the local registry
for remote_image in ${required_images[@]}; do
	has_image=$(docker images ${remote_image} -q)
	if [[ -n "$has_image" ]]; then
		echo "Image $remote_image exists"
	else
		docker pull $remote_image
	fi

	local_image=$(echo $remote_image | sed -e 's/^.*\//localhost:5000\//g')
	if [[ $local_image != *"/"* ]]; then
	  # "${local_image}: This image has no repo in the tag so we need special treatment"
	  local_image="localhost:5000/${local_image}"

	fi
	echo "$Local image: ${local_image}"
	echo "Tagging and pushing..."
	docker tag $remote_image $local_image 
	docker push $local_image

done 