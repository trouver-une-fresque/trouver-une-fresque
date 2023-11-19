import json
import numpy as np
import pandas as pd

from scraper.fdc import get_fdc_data
from scraper.fec import get_fec_data
from scraper.billetweb import get_billetweb_data
from scraper.eventbrite import get_eventbrite_data
from scraper.glide import get_glide_data
from db.etl import etl
from utils.utils import get_config


def main(headless=False):
    tot_records = []

    # Glide
    glide_records = get_glide_data(dr=get_config("webdriver"), headless=headless)
    tot_records += glide_records

    # Eventbrite
    eventbrite_records = get_eventbrite_data(
        dr=get_config("webdriver"), headless=headless
    )
    tot_records += eventbrite_records

    # Fresque de l'Economie Circulaire (WIX)
    fec_records = get_fec_data(dr=get_config("webdriver"), headless=headless)
    tot_records += fec_records

    # Fresque du Climat
    fdc_records = get_fdc_data(dr=get_config("webdriver"), headless=headless)
    tot_records += fdc_records

    # Billetweb
    billetweb_records = get_billetweb_data(
        dr=get_config("webdriver"), headless=headless
    )
    tot_records += billetweb_records

    return pd.DataFrame(tot_records)


if __name__ == "__main__":  # pragma: no cover
    main()
