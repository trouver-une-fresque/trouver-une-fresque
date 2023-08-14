import json
import argparse
import pandas as pd
import psycopg2

from db.etl import execute_values, truncate
from utils.utils import get_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--truncate-first",
        action="store_true",
        default=False,
        help="truncate db before inserting again",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="input json file to be inserted in db",
        required=True,
    )
    args = parser.parse_args()

    credentials = get_config()
    host = credentials["host"]
    port = credentials["port"]
    user = credentials["user"]
    psw = credentials["psw"]
    database = credentials["database"]

    conn = psycopg2.connect(
        database=database, user=user, password=psw, host=host, port=port
    )

    input_records = open(args.input, "r")
    input_records = json.loads(input_records.read())
    df = pd.DataFrame.from_dict(pd.json_normalize(input_records), orient="columns")
    print(df)

    if args.truncate_first:
        truncate(conn, "auth.events_future")

    execute_values(conn, df, "auth.events_future")
