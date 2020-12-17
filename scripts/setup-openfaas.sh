helm repo add openfaas https://openfaas.github.io/faas-netes/

helm template openfaas openfaas/openfaas \
    --namespace openfaas  \
    --set functionNamespace=openfaas-fn \
    --set gateway.directFunctions=true \
    --set gateway.replicas=2 \
    --set generateBasicAuth=true > manifests/base/openfaas.yml

kubectl apply -f manifests/base/openfaas.yaml
PASSWORD=$(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)
export OPENFAAS_PASSWORD=${PASSWORD}
export OPENFAAS_URL=http://localhost:31112
echo -n ${OPENFAAS_PASSWORD} | faas-cli login -g ${OPENFAAS_URL} -u admin --password-stdin
kubectl rollout status deploy/gateway -n openfaas
docker build -t matzhaugen/starlette-backend starlette-backend
faas push -f starlette-backend.yml
faas deploy -f starlette-backend.yml
echo "OpenFaaS url: ${OPENFAAS_URL}"
echo "OpenFaaS admin password: ${PASSWORD}"

kubectl port-forward svc/gateway -n openfaas 31112:8080