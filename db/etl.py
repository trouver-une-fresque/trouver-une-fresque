import psycopg2
import numpy as np
import psycopg2.extras as extras
import pandas as pd
from time import sleep
import json


def execute_values(conn, df, table):
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ','.join(list(df.columns))

    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    print(query)
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()


def truncate(conn, table):
    query = "TRUNCATE TABLE %s" % table
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()


def etl(df):
    file = open('config.json', 'r')
    file = json.loads(file.read())
    credentials = dict(file)

    df = df.astype(str)

    host = credentials['host']
    port = credentials['port']
    user = credentials['user']
    psw = credentials['psw']
    database = credentials['database']

    conn = psycopg2.connect(
        database=database, user=user, password=psw, host=host, port=port
    )

    # Diff entre events et df. Pour les events dans events et pas dans df, si
    # leur start_date+start_time < maintenant, les ajouter dans table past_events

    # Insert all events to the historical table
    execute_values(conn, df, 'auth.events_scrapped')

    # Delete all future events before inserting them again, so that they are
    # updated
    truncate(conn, 'auth.events_future')
    execute_values(conn, df, 'auth.events_future')

    conn.close()
