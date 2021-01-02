import os
from datetime import date, datetime

import boto3
import numpy as np
import pandas as pd
import psycopg2
from pgcopy import CopyManager
from src.config import config
from src.db import crud
from src.db.database import SessionLocal, engine, get_psycopg2_conn


def get_client():
    session = boto3.session.Session()
    client = session.client(
        "s3",
        region_name="nyc3",
        endpoint_url="https://nyc3.digitaloceanspaces.com",
        aws_access_key_id=os.getenv("SPACES_KEY"),
        aws_secret_access_key=os.getenv("SPACES_SECRET"),
    )

    return client


def list_files(client, bucket, prefix):

    response = client.list_objects(Bucket=bucket, Prefix=prefix)
    keys = [obj["Key"] for obj in response["Contents"]]

    return keys


def download_file_to_path(client, bucket, from_path, to_path):
    client.download_file(bucket, from_path, to_path)


# Ingest wiki data from the WIKI/PRICES table at quandl
def ingest_wiki_data(config):
    client = get_client()
    keys = list_files(client, bucket="concord", prefix="quandl_close")
    filenames = []
    for key in keys:
        if not key.endswith(".csv"):
            continue
        filename = key.split("/")[-1]
        if not os.path.exists(str(filename)):
            download_file_to_path(client, "concord", key, str(filename))
        filenames.append(filename)

    print("Files downloaded")

    db = SessionLocal()
    for filename in filenames:
        print("inserting data from", filename)
        data = pd.read_csv(filename)
        cols = ("ticker", "date", "close")
        records = data.to_records(index=False)
        records["date"] = records["date"].astype("M8[D]").astype(date)
        conn = get_psycopg2_conn()
        mgr = CopyManager(conn, "stocks", cols)
        mgr.copy(records)
        conn.commit()

    db.close()


def ingest_metadata(config):
    client = get_client()
    download_file_to_path(
        client, "concord", "metadata/EOD_metadata.csv", "metadata.csv"
    )
    meta = pd.read_csv("metadata.csv")
    cols = ("ticker", "name", "description", "refreshed_at", "from_date", "to_date")
    recarr = meta.to_records(index=False)
    recarr["refreshed_at"] = (
        pd.to_datetime(recarr["refreshed_at"]).to_numpy().astype("M8[D]").astype(date)
    )
    recarr["from_date"] = (
        pd.to_datetime(recarr["from_date"]).to_numpy().astype("M8[D]").astype(date)
    )
    recarr["to_date"] = (
        pd.to_datetime(recarr["to_date"]).to_numpy().astype("M8[D]").astype(date)
    )
    conn = get_psycopg2_conn()
    mgr = CopyManager(conn, "stock_metadata", cols)
    mgr.copy(recarr)
    conn.commit()


if __name__ == "__main__":
    # ingest_wiki_data(config)
    ingest_metadata(config)
