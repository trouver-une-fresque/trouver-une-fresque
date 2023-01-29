import json
import argparse
import pandas as pd
import psycopg2

from db.etl import execute_values

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        help="input json file to be inserted in db"
    )
    args = parser.parse_args()

    file = open('config.json', 'r')
    file = json.loads(file.read())
    credentials = dict(file)
    host = credentials['host']
    port = credentials['port']
    user = credentials['user']
    psw = credentials['psw']
    database = credentials['database']

    conn1 = psycopg2.connect(
        database=database, user=user, password=psw, host=host, port=port
    )

    input_records = open(args.input, 'r')
    input_records = json.loads(input_records.read())
    df = pd.DataFrame.from_dict(pd.json_normalize(input_records), orient='columns')
    print(df)

    execute_values(conn1, df, "events")