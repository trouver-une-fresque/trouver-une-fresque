import json
import argparse
import pandas as pd
import numpy as np

from datetime import datetime

from scraper.fdc import get_fdc_data
from scraper.billetweb import get_billetweb_data
from scraper.eventbrite import get_eventbrite_data
from db.etl import etl
from utils.utils import get_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="run scraping in headless mode",
    )
    args = parser.parse_args()

    fdc_records = get_fdc_data(dr=get_config("webdriver"), headless=args.headless)
    billetweb_records = get_billetweb_data(
        dr=get_config("webdriver"), headless=args.headless
    )
    # eventbrite_records = get_eventbrite_data(
    #    dr=credentials["webdriver"], headless=args.headless
    # )

    tot_records = fdc_records + billetweb_records
    df = pd.DataFrame(tot_records)

    # df['location'] = df['location'].str.strip()
    df["location_name"] = df["location_name"].str.strip()
    df["address"] = df["address"].str.strip()
    df["city"] = df["city"].str.strip()
    df["scrape_date"] = (
        pd.to_datetime("now", utc=True).tz_convert(get_config("timezone")).isoformat()
    )

    # etl(df)

    dt = datetime.now()
    insert_time = dt.strftime("%Y%m%d_%H%M%S")

    with open(f"results/events_{insert_time}.json", "w", encoding="UTF-8") as file:
        df.to_json(file, orient="records", force_ascii=False)


if __name__ == "__main__":  # pragma: no cover
    main()
