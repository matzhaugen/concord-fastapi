
# This script will deploy the concord app to any cluster the kubeconfig is pointing at
kubectl create namespace concord

# Ingress with ambassador
kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml
kubectl apply -f https://github.com/datawire/ambassador-operator/releases/latest/download/ambassador-operator-crds.yaml
kubectl apply -n ambassador -f https://github.com/datawire/ambassador-operator/releases/latest/download/ambassador-operator-kind.yaml
kubectl wait --timeout=180s -n ambassador --for=condition=deployed ambassadorinstallations/ambassador

# Depoy manifests, ENV=[local, dev], which environment to deploy to
kubectl kustomize manifests/${ENV} > manifests/${ENV}.yaml
kubectl apply -f manifests/${ENV}/${ENV}.yaml