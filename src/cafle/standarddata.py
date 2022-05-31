import os
import pandas as pd

__all__ = ['read_standard_process_rate_table']

def read_standard_process_rate_table(colno=None, tolist=False):
    DIRECTORY = '/'.join(os.path.abspath(__file__).split('/')[:-1])
    filename = "/standard_data/standard_process_rate_table.csv"
    fileloc = DIRECTORY + filename

    result = pd.read_csv(fileloc, index_col="idx")

    if colno is None:
        return result
    else:
        colno = str(colno)
        result = result[colno].dropna(axis=0)
        if tolist is False:
            return result
        if tolist is True:
            return result.values.tolist()