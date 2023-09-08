import requests
import numpy as np
import pandas as pd
import time
import json

from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from scraper.records import get_record_dict
from utils.readJson import get_address_data, strip_zip_code
from utils.utils import get_config


def get_eventbrite_data(dr, headless=False):
    print("Scraping data from eventbrite.fr")

    options = FirefoxOptions()
    options.headless = headless

    driver = webdriver.Firefox(options=options, executable_path=dr)

    webSites = [
        {
            # 2tonnes
            "url": "https://www.eventbrite.fr/o/2-tonnes-29470123869",
            "id": 100,
        },
    ]

    records = []

    for page in webSites:
        print(f"==================\nProcessing page {page}")
        driver.get(page["url"])
        driver.implicitly_wait(5)

        while True:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "#events div.organizer-profile__show-more > button",
                        )
                    )
                )
                driver.execute_script("arguments[0].click();", element)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.implicitly_wait(2)
            except:
                break

        driver.execute_script("window.scrollTo(0, 0);")

        elements = []
        future_events = driver.find_element(
            By.CSS_SELECTOR, 'div[data-testid="organizer-profile__future-events"]'
        )
        event_card_divs = future_events.find_elements(By.CSS_SELECTOR, "div.eds-card")

        for event_card_div in event_card_divs:
            link_elements = event_card_div.find_elements(
                By.CSS_SELECTOR, "a.eds-event-card-content__action-link"
            )
            elements.extend(link_elements)

        links = []
        for link_element in elements:
            href = link_element.get_attribute("href")
            if href:
                links.append(href)
        links = np.unique(links)

        print(links, len(links))

        for link in links:
            print(f"\n-> Processing {link} ...")
            driver.get(link)
            driver.implicitly_wait(3)

            ################################################################
            # Has it expired?
            ################################################################
            try:
                if driver.find_elements(By.CSS_SELECTOR, "div.expired-event"):
                    print("Rejecting record: event expired")
                    continue
            except:
                pass

            ################################################################
            # Is there only one event
            ################################################################
            if driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'Sélectionnez') or contains(text(), 'Sélectionner')]",
            ):
                print("Rejecting record: multiple events")
                continue

            ################################################################
            # Parse event title
            ################################################################
            title_el = driver.find_element(
                by=By.TAG_NAME,
                value="h1",
            )
            title = title_el.text

            ################################################################
            # Parse start and end dates
            ################################################################
            date_info_el = driver.find_element(
                by=By.CSS_SELECTOR,
                value="div.date-info",
            )
            event_time = date_info_el.text

            months = {
                "janv.": 1,
                "févr.": 2,
                "mars": 3,
                "avr.": 4,
                "mai": 5,
                "juin": 6,
                "juil.": 7,
                "août": 8,
                "sept.": 9,
                "oct.": 10,
                "nov.": 11,
                "déc.": 12,
            }

            try:
                parts = event_time.split()
                day = int(parts[1])
                month = months[parts[2]]
                year = int(parts[3])
                start_time = parts[4]
                end_time = parts[6]

                # Convert time strings to datetime objects
                event_start_datetime = datetime(
                    year,
                    month,
                    day,
                    int(start_time.split(":")[0]),
                    int(start_time.split(":")[1]),
                )
                event_end_datetime = datetime(
                    year,
                    month,
                    day,
                    int(end_time.split(":")[0]),
                    int(end_time.split(":")[1]),
                )
            except:
                print("Rejecting record: bad date format")
                continue

            ###########################################################
            # Is it an online event?
            ################################################################
            online = False
            try:
                online_el = driver.find_element(
                    By.CLASS_NAME, "p.location-info__address-text"
                )
                if "Online" in online_el.text:
                    online = True
            except NoSuchElementException:
                pass

            ################################################################
            # Location data
            ################################################################
            full_location = ""
            location_name = ""
            address = ""
            city = ""
            department = ""
            longitude = ""
            latitude = ""
            zip_code = ""

            if not online:
                location_el = driver.find_element(
                    By.CSS_SELECTOR, "div.location-info__address"
                )
                full_location = location_el.text

            ################################################################
            # Description
            ################################################################
            description_title_el = driver.find_element(
                By.CSS_SELECTOR, "div.eds-text--left"
            )
            description = description_title_el.text

            ################################################################
            # Parse tickets link
            ################################################################
            tickets_link = link

            ################################################################
            # Building final object
            ################################################################
            record = get_record_dict(
                "",  # f"{page['id']}-{uuids[0]}",
                page["id"],
                title,
                event_start_datetime,
                event_end_datetime,
                full_location,
                location_name,
                address,
                city,
                department,
                zip_code,
                latitude,
                longitude,
                online,
                "",  # training,
                "",  # sold_out,
                "",  # kids,
                link,
                tickets_link,
                description,
            )

            records.append(record)
            print(f"Successfully scraped {link}\n{json.dumps(record, indent=4)}")

    driver.quit()

    return records
