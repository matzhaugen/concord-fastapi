import pandas as pd
import time
import sys
import os

debug = False

CSV_FILE = f"{os.getcwd()}/dataSang.csv"
BACKEND_NAME = "backend"


def get_data(tickers=None, end_date=None):

    start = time.time()
    print(sys.path)
    if tickers is None:
        data = pd.read_csv(CSV_FILE, index_col=0)
    else:
        data = pd.read_csv(CSV_FILE, index_col=0)[tickers]

    data.index = pd.to_datetime(data.index, yearfirst=True)
    data = data[:end_date]
    end = time.time()
    print("Fetched data in {} sec".format(end - start))
    return data
