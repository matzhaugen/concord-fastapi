import time


def handle(event, context):
    time.sleep(0.5)
    return {"statusCode": 200, "body": {"hello": "Hello from OpenFaaS!", "result": event.body}}
