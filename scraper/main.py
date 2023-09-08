import json
import psycopg2
import numpy as np
import pandas as pd

from datetime import datetime

from scraper.fdc import get_fdc_data
from scraper.billetweb import get_billetweb_data
from scraper.eventbrite import get_eventbrite_data
from db.etl import etl
from utils.utils import get_config


def main(headless=False, push_to_db=False):
    tot_records = []

    # Fresque du Climat
    fdc_records = get_fdc_data(dr=get_config("webdriver"), headless=headless)
    tot_records += fdc_records

    # Billetweb
    billetweb_records = get_billetweb_data(
        dr=get_config("webdriver"), headless=headless
    )
    tot_records += billetweb_records

    # Eventbrite
    # eventbrite_records = get_eventbrite_data(
    #   dr=get_config("webdriver"), headless=headless
    # )
    # tot_records += eventbrite_records

    df = pd.DataFrame(tot_records)

    dt = datetime.now()
    insert_time = dt.strftime("%Y%m%d_%H%M%S")
    with open(f"results/events_{insert_time}.json", "w", encoding="UTF-8") as file:
        df.to_json(file, orient="records", force_ascii=False)

    if push_to_db:
        print("Pushing scraped results into db...")
        credentials = get_config()
        host = credentials["host"]
        port = credentials["port"]
        user = credentials["user"]
        psw = credentials["psw"]
        database = credentials["database"]

        conn = psycopg2.connect(
            database=database, user=user, password=psw, host=host, port=port
        )

        etl(conn, df)
        print("Done")

        conn.close()


if __name__ == "__main__":  # pragma: no cover
    main()
