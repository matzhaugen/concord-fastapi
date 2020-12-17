#!/bin/sh
kind delete cluster
set -o errexit

# create registry container unless it already exists
reg_name='kind-registry'
reg_port='5000'
running="$(docker inspect -f '{{.State.Running}}' "${reg_name}" 2>/dev/null || true)"
if [ "${running}" != 'true' ]; then
  docker run \
    -d --restart=always -p "${reg_port}:5000" --name "${reg_name}" \
    registry:2
fi

# create a cluster with the local registry enabled in containerd
# and two nodes, one with a label
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:${reg_port}"]
    endpoint = ["http://${reg_name}:${reg_port}"]
nodes:
- role: control-plane 
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
# port forward 8001 on the host to 8001 on this node
  extraPortMappings:
  - containerPort: 80 # for app testing
    hostPort: 80
    protocol: TCP
  - containerPort: 443 # not currently used
    hostPort: 443
    protocol: TCP
  - containerPort: 31112 # for openfaas testing
    hostPort: 31112
    protocol: TCP
  # add a mount from /path/to/my/files on the host to /files on the node
  extraMounts:
  - hostPath: `pwd`
    containerPath: /concord-fastapi
EOF

# connect the registry to the cluster network
has_kind_network=$(docker network ls -q -f name=kind)
docker network connect "kind" "${reg_name}" || (echo "${reg_name} already connected to the kind network"; true)

# tell https://tilt.dev to use the registry
# https://docs.tilt.dev/choosing_clusters.html#discovering-the-registry
echo "Assigning the local docker registry to each node..."
for node in $(kind get nodes); do
  kubectl annotate node "${node}" "kind.x-k8s.io/registry=localhost:${reg_port}";
done

