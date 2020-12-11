import os
import sys
import time

import pandas as pd

debug = False

CSV_FILE = f"{os.path.dirname(__file__)}/flatData.csv"
BACKEND_NAME = "backend"


def get_data(tickers=None, end_date=None):

    start = time.time()
    data = pd.read_csv(CSV_FILE)
    data = data.pivot(columns="ticker", index="date", values="price")
    data.index = pd.to_datetime(data.index, yearfirst=True)
    if end_date:
        data = data.loc[:end_date]
    end = time.time()
    print("Fetched data in {} sec".format(end - start))
    return data
