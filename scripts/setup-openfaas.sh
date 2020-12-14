helm repo add openfaas https://openfaas.github.io/faas-netes/

helm template openfaas openfaas/openfaas \
    --namespace openfaas  \
    --set functionNamespace=openfaas-fn \
    --set gateway.directFunctions=true \
    --set gateway.replicas=4 \
    --set generateBasicAuth=true > manifests/openfaas.yml

kubectl apply -f manifests/openfaas.yml
PASSWORD=$(kubectl -n openfaas get secret basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)
export OPENFAAS_PASSWORD=${PASSWORD}
export OPENFAAS_URL=http://localhost:31112
kubectl rollout status deploy/gateway -n openfaas
faas up -f of-concord-fastapi.yml
echo "OpenFaaS url: ${OPENFAAS_URL}"
echo "OpenFaaS admin password: ${PASSWORD}"
echo -n ${OPENFAAS_PASSWORD} | faas-cli login -g ${OPENFAAS_URL} -u admin --password-stdin
kubectl port-forward svc/gateway -n openfaas 8086:8080