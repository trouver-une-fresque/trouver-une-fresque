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
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("the dataframe is inserted")
    cursor.close()


def etl(df):
    file = open('config.json', 'r')
    file = json.loads(file.read())
    credentials = dict(file)

    df = df.astype(str)
    # columns = list( df.columns.values)

    # nr_val = '?,'*len(columns)
    # nr_val = nr_val[:-1]

    host = credentials['host']
    port = credentials['port']
    user = credentials['user']
    psw = credentials['psw']
    database = credentials['database']
    table_schema = credentials['table_schema']

    if table_schema != '':
        table_schema = table_schema+'.'

    print("Truncating old data\n")

    conn1 = psycopg2.connect(
        database=database, user=user, password=psw, host=host, port=port
    )

    conn1.autocommit = True
    cursor = conn1.cursor()

    truncate_sql = f'''truncate table {table_schema}event_data;
			truncate table {table_schema}event_data_main;
	'''

    cursor.execute(truncate_sql)

    conn1.commit()
    conn1.close()

    conn = psycopg2.connect(
        database=database, user=user, password=psw, host=host, port=port
    )
    execute_values(conn, df, table_schema+'event_data')

    conn2 = psycopg2.connect(
        database=database, user=user, password=psw, host=host, port=port
    )
    conn2.autocommit = True
    cursor = conn2.cursor()
    try:
        insert_sql = f'''

	Insert into {table_schema}event_data_main
		SELECT
				online       :: boolean 
				,training    :: boolean 
                ,sold_out        :: boolean 
				,(case when start_date='' then null else start_date end)   :: date as start_date 
				,(case when start_time='' then null else start_time end)   :: time as start_time
				,(case when end_date  ='' then null else end_date end)     :: date as end_date 
				,(case when end_time  ='' then null else end_time end)	   :: time as end_time
				,scrape_date :: timestamp 
				,zip_code
				,latitude
				,longitude
				,source_link
				,tickets_link
				,description
				,department
				,title
				,location
				,location_name
				,address
				,city
				,workshop_type	
		FROM {table_schema}event_data;


	Insert into {table_schema}event_historical_data
		SELECT
			online       :: boolean 
			,training    :: boolean 
            ,sold_out        :: boolean 
			,(case when start_date='' then null else start_date end)   :: date as start_date 
			,(case when start_time='' then null else start_time end)   :: time as start_time
			,(case when end_date  ='' then null else end_date end)     :: date as end_date 
			,(case when end_time  ='' then null else end_time end)	   :: time as end_time
			,scrape_date :: timestamp 
			,zip_code
			,latitude
			,longitude
			,source_link
			,tickets_link
			,description
			,department
			,title
			,location
			,location_name
			,address
			,city
			,workshop_type	
		FROM {table_schema}event_data;

		'''

        cursor.execute(insert_sql)

        conn2.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()

    conn2.close()
