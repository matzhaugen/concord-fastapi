echo -n ${OPENFAAS_PASSWORD} | faas-cli login -g ${OPENFAAS_URL} -u admin --password-stdin || echo "Please login to the openfaas cluster first"
faas template pull https://github.com/openfaas-incubator/python-flask-template
faas new --lang python3-http-debian of-concord