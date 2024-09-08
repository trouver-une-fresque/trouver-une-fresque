import pandas as pd

from scraper.fdc import get_fdc_data
from scraper.fec import get_fec_data
from scraper.billetweb import get_billetweb_data
from scraper.eventbrite import get_eventbrite_data
from scraper.glide import get_glide_data
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from utils.utils import get_config


def main(headless=False):
    records = []

    service = Service(executable_path=get_config("webdriver"))
    options = FirefoxOptions()
    options.set_preference("intl.accept_languages", "en-us")
    if headless:
        options.add_argument("-headless")

    records += get_billetweb_data(service=service, options=options)
    records += get_glide_data(service=service, options=options)
    records += get_eventbrite_data(service=service, options=options)
    records += get_fec_data(service=service, options=options)
    records += get_fdc_data(service=service, options=options)

    return pd.DataFrame(records)


if __name__ == "__main__":
    main()
