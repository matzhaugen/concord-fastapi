import os
import sys
import time

import pandas as pd

debug = False

CSV_FILE = f"{os.path.dirname(__file__)}/flatData.csv"
BACKEND_NAME = "backend"


def get_data(tickers=None, start_date=None, end_date=None):

    if end_date and start_date:
        assert end_date > start_date, "End date must be greater than start date"
    start = time.time()
    data = pd.read_csv(CSV_FILE)
    data = data.pivot(columns="ticker", index="date", values="close")
    if tickers:
        data = data[tickers]
    data.index = pd.to_datetime(data.index, yearfirst=True)
    if end_date:
        data = data.loc[:end_date]
    if start_date:
        data = data.loc[start_date:]
    end = time.time()
    print("Fetched data in {} sec".format(end - start))
    return data
