
# Concord portfolio optimizer
Welcome!
This repo is an app that will determine how a given portfolio should be weighted.

Currently the main app is located in the `concord` folder, which relies on a backend in the `backend` folder. The backend will be replaced with something that scales.

## Run locally
Make sure port 80 and 81 are free for use. Then, in the root of the repo, type
```
make server
```
Now your server is running on 80 with a backend on 81.

To see the api documentation go to your browser and type `localhost:80/docs`.

## Example requests

After starting the server (see section above),
```
curl localhost:80/tickers
```

```
curl -X POST -d '{"tickers": ["AA","AXP"], "endDate": "1993-01-01"}' localhost:80/portfolio
```

## How to scale this

Because the backend is just an http server this will not scale well. Instead a serveless function could be the way to go, for example using [openfaas](https://www.openfaas.com/).

There might be other ideas, like a Kubernetes Deployment with a pubsub subscriber and scaling by the number of undelivered pubsub messages.

## Developing using openfaas functions

```
faas build -f of-concord.yml # build the openfaas function
make build # build the 
make server
```

The first step will make sure that the latest files from the `of-concord` folder is copied into the `build` folder with the latest dockerfile which is the target of the docker-compose file. The `make build` step will then build the docker-compose images do you can develop locally. `make server` will launch the docker-compose server so you can test with direct curl, pytest or with a full blown front end.

## Testing the app

We test the concord backend app as follows
```
make server # In one window
make test-concord # In a new window
```

## Launching the front end

```
make frontend
```

### Running on a local cluster

This requires [KinD](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).

A nice-to-have is [k9s](https://github.com/derailed/k9s) for detailed monitoring of the cluster.

Setup cluster with ingress from localhost.
```
make kind
```
This will take a few minutes.

Then try
```
curl localhost/tickers
curl -X POST -d '{"tickers": ["AA","AXP"], "endDate": "1993-01-01"}' localhost/portfolio
```


### GCS cloud run deployment
Example commands to deploy the backend to a google cloud run dervice.
```
gcloud auth configure-docker
cd backend && docker build -t eu.gcr.io/experiment-ml-tk/hello-run .
docker push eu.gcr.io/experiment-ml-tk/hello-run
gcloud run deploy --image gcr.io/experiment-ml-tk/hello-run --platform managed
```