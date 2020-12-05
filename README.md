
# Concord portfolio optimizer
Welcome!
This repo is an app that will determine how a given portfolio should be weighted.

## Run locally
Make sure port 8000 and 8001 are free for use. Then, in the root of the repo, type
```
make server
```
Now your server is running on 8001 with a backend on 8000.

To see the api documentation go to your browser and type `localhost:8001/docs`.

## Example requests

```
curl localhost:8001/tickers
```

```
curl -X POST -d '{"tickers": ["AA","AXP"], "endDate": "1993-01-01"}' localhost:8001/portfolio
```

## How to scale this

Because the backend is just an http server this will not scale well. Instead a serveless function could be the way to go, for example using [openfaas](https://www.openfaas.com/).

There might be other ideas, like a Kubernetes Deployment with a pubsub subscriber and scaling by the number of undelivered pubsub messages.


### GCS cloud run deployment
Example commands to deploy the backend to a google cloud run dervice.
```
gcloud auth configure-docker
cd backend && docker build -t eu.gcr.io/experiment-ml-tk/hello-run .
docker push eu.gcr.io/experiment-ml-tk/hello-run
gcloud run deploy --image gcr.io/experiment-ml-tk/hello-run --platform managed
```