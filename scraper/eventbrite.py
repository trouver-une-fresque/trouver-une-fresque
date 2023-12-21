import requests
import numpy as np
import pandas as pd
import time
import json
import re

from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from db.records import get_record_dict
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

        # Reject all cookies
        try:
            overlay = driver.find_element(By.CSS_SELECTOR, "#consentManagerMainDialog")
            if overlay.is_displayed():
                overlay.find_element(By.CSS_SELECTOR, "#_evidon-decline-button").click()
        except NoSuchElementException:
            pass

        more_content = True
        while more_content:
            print(f"Scrolling to the bottom...")
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.implicitly_wait(2)
                time.sleep(2)
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "div.organizer-profile__section--content div.organizer-profile__show-more > button",
                        )
                    )
                )
                desired_y = (next_button.size["height"] / 2) + next_button.location["y"]
                window_h = driver.execute_script("return window.innerHeight")
                window_y = driver.execute_script("return window.pageYOffset")
                current_y = (window_h / 2) + window_y
                scroll_y_by = desired_y - current_y
                driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)
                time.sleep(2)
                next_button.click()
            except TimeoutException:
                more_content = False
            except Exception as e:
                print(f"Had to break: {type(e)}")
                break

        driver.execute_script("window.scrollTo(0, 0);")

        elements = []
        future_events = driver.find_element(
            By.CSS_SELECTOR, 'div[data-testid="organizer-profile__future-events"]'
        )
        event_card_divs = future_events.find_elements(By.CSS_SELECTOR, "div.event-card")

        print(f"Found {len(event_card_divs)} events")

        for event_card_div in event_card_divs:
            link_elements = event_card_div.find_elements(
                By.CSS_SELECTOR, "a.event-card-link"
            )
            elements.extend(link_elements)

        links = []
        for link_element in elements:
            href = link_element.get_attribute("href")
            if href:
                links.append(href)
        links = np.unique(links)

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
                "//button[contains(text(), 'Sélectionnez') or contains(text(), 'Sélectionner') or contains(text(), 'Select')]",
            ):
                print("Rejecting record: multiple events")
                continue

            ################################################################
            # Parse event id
            ################################################################
            uuids = re.search(r"/e/([^/?]+)", link)
            if not uuids:
                print("Rejecting record: UUID not found")
                continue

            ################################################################
            # Parse event title
            ################################################################
            title_el = driver.find_element(
                by=By.TAG_NAME,
                value="h1",
            )
            title = title_el.text

            if "plénière" in title.lower():
                print("Rejecting record: plénière")
                continue

            ################################################################
            # Parse start and end dates
            ################################################################
            try:
                date_info_el = driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="div.date-info",
                )
                event_time = date_info_el.text
            except NoSuchElementException:
                print("Rejecting record: no dates")
                continue

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
                    By.CSS_SELECTOR, "p.location-info__address-text"
                )
                online_list = ["online", "en ligne", "distanciel"]
                online = any(w in online_el.text.lower() for w in online_list)
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
                full_location_text = location_el.text.split("\n")
                location_name = full_location_text[0]
                address_and_city = full_location_text[1]
                full_location = f"{location_name}, {address_and_city}"

                pattern = r"^(.*?)\s+(\d{5})\s+(.*?)$"
                match = re.match(pattern, address_and_city)
                if match:
                    address = match.group(1)
                    zip_code = match.group(2)
                    city = match.group(3)
                else:
                    print("Rejecting record: bad address format")
                    continue

                ############################################################
                # Localisation sanitizer
                ############################################################
                try:
                    search_query = f"{address}, {city}, France"
                    address_dict = get_address_data(search_query)
                except json.JSONDecodeError:
                    print(
                        f"Rejecting record: error while parsing the national address API response"
                    )
                    continue

                department = address_dict.get("cod_dep", "")
                longitude = address_dict.get("longitude", "")
                latitude = address_dict.get("latitude", "")
                zip_code = address_dict.get("postcode", "")

                if department == "":
                    print("Rejecting record: no result from the national address API")
                    driver.back()
                    wait = WebDriverWait(driver, 10)
                    iframe = wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                    )
                    driver.switch_to.frame(iframe)
                    continue

            ################################################################
            # Description
            ################################################################
            description_title_el = driver.find_element(
                By.CSS_SELECTOR, "div.eds-text--left"
            )
            description = description_title_el.text

            ################################################################
            # Training?
            ################################################################
            training_list = ["formation", "briefing", "animateur"]
            training = any(w in title.lower() for w in training_list)

            ################################################################
            # Is it full?
            ################################################################
            tickets_link_el = driver.find_element(
                By.CSS_SELECTOR, "div.conversion-bar__panel-info"
            )
            sold_out = (
                "complet" in tickets_link_el.text.lower()
                or "ventes achevées" in tickets_link_el.text.lower()
            )

            ################################################################
            # Is it suited for kids?
            ################################################################
            kids = False

            ################################################################
            # Parse tickets link
            ################################################################
            tickets_link = link

            ################################################################
            # Building final object
            ################################################################
            record = get_record_dict(
                f"{page['id']}-{uuids.group(1)}",
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
                training,
                sold_out,
                kids,
                link,
                tickets_link,
                description,
            )

            records.append(record)
            print(f"Successfully scraped {link}\n{json.dumps(record, indent=4)}")

    driver.quit()

    return records
