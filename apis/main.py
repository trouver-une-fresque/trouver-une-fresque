import pandas as pd

from apis.glorieuses import get_glorieuses_data


def main():
    tot_records = []

    glorieuses_api_records = get_glorieuses_data()
    tot_records += glorieuses_api_records

    return pd.DataFrame(tot_records)
