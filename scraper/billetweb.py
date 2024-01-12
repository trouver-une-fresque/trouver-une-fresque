import numpy as np
import time
import pandas as pd
import requests
import re
import json
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from geopy.geocoders import Nominatim
from geopy import geocoders
from dateutil.parser import *

from db.records import get_record_dict
from utils.readJson import get_address_data, strip_zip_code


def get_billetweb_data(dr, headless=False):
    print("Scraping data from www.billetweb.fr")

    service = Service(executable_path=dr)
    options = FirefoxOptions()
    options.set_preference("intl.accept_languages", "en-us")
    options.headless = headless
    driver = webdriver.Firefox(service=service, options=options)

    webSites = [
        {
            # Fresque des Nouveaux Récits
            "url": "https://www.billetweb.fr/pro/fdnr",
            "iframe": "event21569",
            "id": 0,
        },
        {
            # Fresque Océane
            "url": "https://www.billetweb.fr/pro/billetteriefo",
            "iframe": "event15247",
            "id": 1,
        },
        {
            # Fresque de la Biodiversité
            "url": "https://www.billetweb.fr/multi_event.php?user=82762",
            "iframe": "event17309",
            "id": 2,
        },
        {
            # Fresque du Numérique
            "url": "https://www.billetweb.fr/multi_event.php?user=84999",
            "iframe": "eventu84999",
            "id": 3,
        },
        {
            # Fresque Agri'Alim
            "url": "https://www.billetweb.fr/pro/fresqueagrialim",
            "iframe": "event11421",
            "id": 4,
        },
        {
            # Fresque de l'Alimentation
            "url": "https://www.billetweb.fr/pro/fresquealimentation",
            "iframe": "event11155",
            "id": 5,
        },
        {
            # Fresque de la Construction
            "url": "https://www.billetweb.fr/pro/fresquedelaconstruction",
            "iframe": "event11574",
            "id": 6,
        },
        {
            # Fresque de la Mobilité
            "url": "https://www.billetweb.fr/pro/fresquedelamobilite",
            "iframe": "event11698",
            "id": 7,
        },
        {
            # Fresque du Sexisme
            "url": "https://www.billetweb.fr/pro/fresque-du-sexisme",
            "iframe": "event27112",
            "id": 8,
        },
        {
            # Atelier OGRE
            "url": "https://www.billetweb.fr/pro/atelierogre",
            "iframe": "event13026",
            "id": 9,
        },
        {
            # Atelier Nos vies bas carbone
            "url": "https://www.billetweb.fr/multi_event.php?user=132897",
            "iframe": "event22230",
            "id": 10,
        },
        {
            # Fresque de l'Eau
            "url": "https://www.billetweb.fr/multi_event.php?user=138110",
            "iframe": "eventu138110",
            "id": 11,
        },
        {
            # futurs proches
            "url": "https://www.billetweb.fr/pro/futursproches",
            "iframe": "event14893",
            "id": 12,
        },
        {
            # Fresque de la Diversité
            "url": "https://www.billetweb.fr/multi_event.php?user=168799",
            "iframe": "eventu168799",
            "id": 13,
        },
        {
            # Fresque du Textile
            "url": "https://www.billetweb.fr/multi_event.php?user=166793",
            "iframe": "event27458",
            "filter": "textile",
            "id": 14,
        },
        {
            # Fresque des Déchets
            "url": "https://www.billetweb.fr/multi_event.php?user=166793",
            "iframe": "event27458",
            "filter": "dechet",
            "id": 15,
        },
    ]

    records = []

    for page in webSites:
        print(f"==================\nProcessing page {page}")
        driver.get(page["url"])
        driver.implicitly_wait(2)

        driver.switch_to.frame(page["iframe"])

        ele = driver.find_elements(By.CSS_SELECTOR, "a.naviguate")
        links = [e.get_attribute("href") for e in ele]

        for link in links:
            if "https://www.billetweb.fr/multi_event.php?&multi" not in link:
                print(f"\n-> Processing {link} ...")
                driver.get(link)
                driver.implicitly_wait(3)

                if "filter" in page:
                    if page["filter"] not in link:
                        print(
                            "Rejecting filter: expected filtering keyword not present in current link"
                        )
                        continue

                try:
                    # Attempt to find the div element by its id
                    description_block = driver.find_element(By.ID, "description_block")
                except NoSuchElementException:
                    print("Rejecting record: no description")
                    continue

                new_ui = False
                try:
                    driver.find_element(
                        By.CSS_SELECTOR,
                        "#description_block > div.event_title > div.event_name",
                    )
                except NoSuchElementException:
                    new_ui = True
                    pass

                try:
                    driver.find_element(By.ID, "more_info").click()
                except:
                    pass

                ################################################################
                # Parse event id
                ################################################################
                uuids = re.search(r"/([^/]+?)&", link)
                if not uuids:
                    print("Rejecting record: UUID not found")
                    continue

                ################################################################
                # Parse event title
                ################################################################
                if new_ui:
                    title_el = driver.find_element(
                        by=By.CSS_SELECTOR, value="#event_title > div.event_name"
                    )
                else:
                    title_el = driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="#description_block > div.event_title > div.event_name",
                    )
                title = title_el.text

                if "cadeau" in title.lower() or "don" in title.lower():
                    print("Rejecting record: gift card")
                    continue

                ################################################################
                # Parse start and end dates
                ################################################################
                if new_ui:
                    time_el = driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="#event_title > div.event_start_time > span.text",
                    )
                    event_time = time_el.text.lower()
                else:
                    time_el = driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="#description_block > div.event_title > span > a > div.event_start_time",
                    )
                    event_time = time_el.text.lower()

                if " from " in event_time and " to " in event_time:
                    """Thu Oct 19, 2023 from 01:00 PM to 02:00 PM"""
                    try:
                        date_and_times = event_time.split(" from ")
                        start_date_string = date_and_times[0]
                        time_range = date_and_times[1].split(" to ")
                        start_time_string = time_range[0]
                        end_time_string = time_range[1]
                    except:
                        print(
                            f"Rejecting record: invalid dates: start_date_string={start_date_string}, start_time_string={start_time_string}, end_time_string={end_time_string}"
                        )
                        continue

                elif " to " in event_time:
                    """Sat Apr 22, 2023 to Sat Sep 02, 2023"""
                    try:
                        dates = event_time.split(" to ")
                        start_date_string = dates[0]
                        end_date_string = dates[1]
                        start_time_string = ""
                        end_time_string = ""
                    except:
                        print(
                            f"Rejecting record: invalid dates: start_date_string={start_date_string}, end_date_string={end_date_string}"
                        )
                        continue

                elif " at " in event_time:
                    event_arr = event_time.split(" at ")
                    try:
                        start_date_string = event_arr[0]
                        start_time_string = event_arr[1]
                        end_time_string = ""
                    except:
                        print(
                            f"Rejecting record: invalid dates: {start_time} (start_time) and {end_time} (end_time)"
                        )
                        continue

                else:
                    """Sat Sep 02, 2023"""
                    # title_el = driver.find_element(
                    #    by=By.CSS_SELECTOR, value='#shop_block > #context_title')
                    # title = title_el.text

                    start_date_string = event_time
                    start_time_string = ""
                    end_time_string = ""

                if start_time_string == "":
                    print(
                        f"The page should be more specific about the event start time."
                    )
                    continue

                event_date = datetime.strptime(start_date_string, "%a %b %d, %Y")
                event_start_time = datetime.strptime(
                    start_time_string, "%I:%M %p"
                ).time()
                event_start_datetime = datetime.combine(event_date, event_start_time)

                if not end_time_string == "":
                    event_end_time = datetime.strptime(
                        end_time_string, "%I:%M %p"
                    ).time()
                    event_end_datetime = datetime.combine(event_date, event_end_time)
                    duration = event_end_datetime - event_start_datetime

                    if duration > timedelta(hours=48):
                        print(
                            f"Rejecting record: event is too long duration={duration}"
                        )
                        continue

                ################################################################
                # Is it an online event?
                ################################################################
                online_list = ["online", "en ligne", "distanciel"]
                online = any(w in title.lower() for w in online_list)
                title = title.replace(" Online event", "")

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
                    try:
                        if new_ui:
                            address_el = driver.find_element(
                                by=By.CSS_SELECTOR, value="div.location_summary"
                            )
                        else:
                            address_el = driver.find_element(
                                by=By.CSS_SELECTOR,
                                value="#page_block_location > div.location > div.location_info > div.address > a",
                            )
                    except:
                        print(f"Rejecting record: empty address")
                        continue

                    full_location = address_el.text

                    # Parse location fields
                    if "," in full_location:
                        loc_arr = full_location.split(",")
                        if len(loc_arr) >= 5:
                            print(
                                f"Rejecting records: address is too long ({len(loc_arr)} parts)"
                            )
                            continue
                        elif len(loc_arr) >= 3:
                            if loc_arr[2].strip().lower() == "france":
                                address = loc_arr[0]
                                city = loc_arr[1]
                            else:
                                location_name = loc_arr[0]
                                address = loc_arr[1]
                                city = loc_arr[2]
                        elif len(loc_arr) == 2:
                            if loc_arr[1].strip().lower() == "france":
                                city = loc_arr[0]
                            else:
                                address = loc_arr[0]
                                city = loc_arr[1]

                    location_name = location_name.strip()
                    address = address.strip()
                    city = strip_zip_code(city)

                    if address == "":
                        print("Rejecting record: empty address")
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
                        print(
                            "Rejecting record: no result from the national address API"
                        )
                        continue

                ################################################################
                # Description
                ################################################################
                try:
                    even_el = driver.find_element(
                        by=By.CSS_SELECTOR, value="#description"
                    )
                except:
                    print(f"Rejecting record: no description")
                    continue
                description = even_el.text

                ################################################################
                # Training?
                ################################################################
                training_list = ["formation", "briefing", "animateur"]
                training = any(w in title.lower() for w in training_list)

                ################################################################
                # Is it full?
                ################################################################
                try:
                    wait = WebDriverWait(driver, 10)
                    iframe = wait.until(
                        EC.frame_to_be_available_and_switch_to_it(
                            (By.CSS_SELECTOR, "#shop_block iframe")
                        )
                    )
                    # Attempt to find the div element by its id
                    remaining_slots_el = driver.find_element(
                        By.CSS_SELECTOR,
                        "div.block",
                    )
                    sold_out = (
                        "aucune" in remaining_slots_el.text
                        or "nombre maximal" in remaining_slots_el.text
                        or "sold out" in remaining_slots_el.text
                    )
                except NoSuchElementException:
                    sold_out = "complet" in title.lower()
                finally:
                    driver.switch_to.default_content()

                ################################################################
                # Is it suited for kids?
                ################################################################
                kids_list = ["kids", "junior", "jeunes"]
                kids = any(w in title.lower() for w in kids_list) and not training

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
                    link,
                    description,
                )

                records.append(record)
                print(f"Successfully scraped {link}\n{json.dumps(record, indent=4)}")

    driver.quit()

    return records
