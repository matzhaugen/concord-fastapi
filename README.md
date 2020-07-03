## Google Cloud Run + fastapi

Quick and dirty experiment with GCR + fastapi demo

Definitely not production ready.

Example commands to run the test service
```shell
$ gcloud auth configure-docker
$ docker build -t eu.gcr.io/experiment-ml-tk/hello-run .
$ docker push eu.gcr.io/experiment-ml-tk/hello-run
$ gcloud run deploy --image gcr.io/experiment-ml-tk/hello-run --platform managed
```