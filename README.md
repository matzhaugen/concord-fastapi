
# Concord portfolio optimizer
Welcome!
This repo is an app that will determine how a given portfolio should be weighted.

## Run locally
Make sure port 8000 and 8001 are free for use. Then, in the root of the repo, type
```
make server
```
Now your server is running on 8000 with a backend on 8001.

To see the api documentation go to your browser and type `localhost:8000/docs`.


## Google Cloud Run 

Quick and dirty experiment with GCR.

Example commands to run the test service
```shell
$ gcloud auth configure-docker
$ docker build -t eu.gcr.io/experiment-ml-tk/hello-run .
$ docker push eu.gcr.io/experiment-ml-tk/hello-run
$ gcloud run deploy --image gcr.io/experiment-ml-tk/hello-run --platform managed
```