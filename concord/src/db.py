import pandas as pd
import time
import sys

debug = False
CSV_FILE = "dataSang.csv"
BACKEND_NAME = "backend"


def get_data(tickers=None):

    start = time.time()
    print(sys.path)
    if tickers is None:
        data = pd.read_csv(CSV_FILE, index_col=0)
    else:
        data = pd.read_csv(CSV_FILE, index_col=0)[tickers]
    end = time.time()
    print("Fetched data in {} sec".format(end - start))
    return data
