import json
import argparse
import pandas as pd
import numpy as np

from datetime import datetime

from scraper.billetweb import get_billetweb_data
from scraper.eventbrite import get_eventbrite_data
from db.etl import etl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="run scraping in headless mode",
    )
    args = parser.parse_args()

    file = open("config.json", "r")
    file = json.loads(file.read())
    credentials = dict(file)

    billetweb_records = get_billetweb_data(
        dr=credentials["chromedriver"], headless=args.headless
    )
    eventbrite_records = get_eventbrite_data(
        dr=credentials["chromedriver"], headless=args.headless
    )

    tot = billetweb_records + eventbrite_records
    df = pd.DataFrame(tot)

    # df['location'] = df['location'].str.strip()
    df["location_name"] = df["location_name"].str.strip()
    df["address"] = df["address"].str.strip()
    df["city"] = df["city"].str.strip()
    df["scrape_date"] = pd.to_datetime("now", utc=True).strftime("%Y-%m-%d %H:%M:%S")

    # etl(df)

    dt = datetime.now()
    insert_time = dt.strftime("%Y%m%d_%H%M%S")

    with open(f"results/events_{insert_time}.json", "w", encoding="UTF-8") as file:
        df.to_json(file, orient="records", force_ascii=False)


if __name__ == "__main__":  # pragma: no cover
    main()
