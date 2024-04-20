import argparse
import pandas as pd
import psycopg

from datetime import datetime
from psycopg.conninfo import make_conninfo

from apis import main as main_apis
from scraper import main as main_scraper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="run scraping in headless mode",
    )
    parser.add_argument(
        "--push-to-db",
        action="store_true",
        default=False,
        help="push the scraped results to db",
    )
    args = parser.parse_args()

    df1 = main_scraper(headless=args.headless)
    df2 = main_apis()
    df_merged = pd.concat([df1, df2])

    dt = datetime.now()
    insert_time = dt.strftime("%Y%m%d_%H%M%S")
    with open(f"results/events_{insert_time}.json", "w", encoding="UTF-8") as file:
        df_merged.to_json(file, orient="records", force_ascii=False, indent=2)

    if args.push_to_db:
        print("Pushing scraped results into db...")
        credentials = get_config()
        host = credentials["host"]
        port = credentials["port"]
        user = credentials["user"]
        psw = credentials["psw"]
        database = credentials["database"]

        with psycopg.connect(
            make_conninfo(dbname=database, user=user, password=psw, host=host, port=port)
        ) as conn:
            etl(conn, df_merged)

        print("Done")
