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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from geopy.geocoders import Nominatim
from geopy import geocoders
from dateutil.parser import *

from scraper.records import get_record_dict
from utils.readJson import get_address_data, strip_zip_code


def get_glide_data(dr, headless=False):
    print("Scraping data from glide.page")

    options = FirefoxOptions()
    options.headless = headless

    driver = webdriver.Firefox(options=options, executable_path=dr)

    webSites = [
        {
            # Fresque des Frontières Planétaires (ateliers)
            "url": "https://1erdegre.glide.page/dl/3b1bc8",
            "id": 500,
        },
        {
            # Fresque des Frontières Planétaires (formations)
            "url": "https://1erdegre.glide.page/dl/dcc150",
            "id": 500,
        },
    ]

    records = []
    current_page = 0

    for page in webSites:
        print(f"==================\nProcessing page {page}")
        driver.get(page["url"])
        driver.implicitly_wait(10)

        ele = driver.find_elements(By.XPATH, '//div[@role="button"]')
        num_el = len(ele)

        for i in range(num_el):
            ele = driver.find_elements(By.XPATH, '//div[@role="button"]')
            el = ele[i]
            el.click()
            time.sleep(5)
            link = driver.current_url
            print(f"\n-> Processing {link} ...")
            driver.implicitly_wait(3)

            ################################################################
            # Parse event id
            ################################################################
            uuid = link.split("/")[-1]
            if not uuid:
                print("Rejecting record: UUID not found")
                driver.back()
                continue

            ################################################################
            # Parse event title
            ################################################################
            title_el = driver.find_element(by=By.TAG_NAME, value="h2")
            title = title_el.text

            ################################################################
            # Parse start and end dates
            ################################################################
            time_el = driver.find_element(
                by=By.XPATH,
                value="//div[contains(@class, 'eXMJmv') and contains(text(), 'Date')]",
            )
            parent_el = time_el.find_element(by=By.XPATH, value="..")
            event_time_el = parent_el.find_element(by=By.XPATH, value="./*[2]")
            event_time = event_time_el.text.lower()

            month_mapping = {
                "janvier": 1,
                "février": 2,
                "mars": 3,
                "avril": 4,
                "mai": 5,
                "juin": 6,
                "juillet": 7,
                "août": 8,
                "septembre": 9,
                "octobre": 10,
                "novembre": 11,
                "décembre": 12,
            }

            year = 2023
            date_and_times = event_time.split(" de ")
            week_day, day, month_string = date_and_times[0].split(" ")

            # Define a regular expression pattern to extract times
            time_pattern = r"(\d{1,2}h\d{2}) à (\d{1,2}h\d{2})"

            # Find matches using the pattern
            matches = re.findall(time_pattern, date_and_times[1])
            if matches:
                start_time, end_time = matches[0]
            else:
                print("Rejecting record: bad format in dates")
                driver.back()
                continue

            # Extract hours and minutes from time strings
            start_hour, start_minute = map(int, start_time.split("h"))
            end_hour, end_minute = map(int, end_time.split("h"))

            # Construct the datetime objects
            event_start_datetime = datetime(
                int(year),
                month_mapping[month_string],
                int(day),
                start_hour,
                start_minute,
            )
            event_end_datetime = datetime(
                int(year),
                month_mapping[month_string],
                int(day),
                end_hour,
                end_minute,
            )

            ################################################################
            # Is it an online event?
            ################################################################
            online_list = ["online", "en ligne", "distanciel"]

            time_label_el = driver.find_element(
                by=By.XPATH,
                value="//div[contains(@class, 'eXMJmv') and contains(text(), 'Format')]",
            )
            parent_el = time_label_el.find_element(by=By.XPATH, value="..")
            online_el = parent_el.find_element(by=By.XPATH, value="./*[2]")
            online = online_el.text.lower()

            online = any(w in online for w in online_list)

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
                    address_label_el = driver.find_element(
                        by=By.XPATH,
                        value="//div[contains(@class, 'eXMJmv') and contains(text(), 'Adresse')]",
                    )
                    parent_el = address_label_el.find_element(by=By.XPATH, value="..")
                    address_el = parent_el.find_element(by=By.XPATH, value="./*[2]")
                except:
                    print(f"Rejecting record: empty address")
                    driver.back()
                    continue

                full_location = address_el.text

                # Parse location fields
                if "," in full_location:
                    loc_arr = full_location.split(",")
                    if len(loc_arr) >= 5:
                        print(
                            f"Rejecting records: address is too long ({len(loc_arr)} parts)"
                        )
                        driver.back()
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
                        zip_code_pattern = r"\b\d{5}\b"
                        zip_code = re.findall(zip_code_pattern, loc_arr[1])
                        zip_code_split = loc_arr[1].strip().split(zip_code[0])
                        zip_code_split = [item for item in zip_code_split if item != ""]
                        if zip_code and len(zip_code_split) > 1:
                            print("Rejecting record: empty address or city")
                            driver.back()
                            continue

                        address = loc_arr[0]
                        city = loc_arr[1]

                location_name = location_name.strip()
                address = address.strip()
                city = strip_zip_code(city)

                if address == "":
                    print("Rejecting record: empty address")
                    driver.back()
                    continue

                ############################################################
                # Localisation sanitizer
                ############################################################
                search_query = f"{address}, {city}, France"
                address_dict = get_address_data(search_query)

                department = address_dict.get("cod_dep", "")
                longitude = address_dict.get("longitude", "")
                latitude = address_dict.get("latitude", "")
                zip_code = address_dict.get("postcode", "")

                if department == "":
                    print("Rejecting record: no result from the national address API")
                    driver.back()
                    continue

            ################################################################
            # Description
            ################################################################
            description_label_el = driver.find_element(
                by=By.XPATH,
                value="//div[contains(@class, 'eXMJmv') and contains(text(), 'Description')]",
            )
            parent_el = description_label_el.find_element(by=By.XPATH, value="..")
            description_el = parent_el.find_element(by=By.XPATH, value="./*[2]")
            description = description_el.text

            ################################################################
            # Training?
            ################################################################
            training_list = ["formation", "briefing", "animateur"]
            training = any(w in title.lower() for w in training_list)

            ################################################################
            # Is it full?
            ################################################################
            attendees_label_el = driver.find_element(
                by=By.XPATH,
                value="//div[contains(@class, 'eXMJmv') and contains(text(), 'participant')]",
            )
            parent_el = attendees_label_el.find_element(by=By.XPATH, value="..")
            attendees_el = parent_el.find_element(by=By.XPATH, value="./*[2]")
            attendees = attendees_el.text

            sold_out = attendees.split("/")[0] == attendees.split("/")[1]

            ################################################################
            # Is it suited for kids?
            ################################################################
            kids = False

            ################################################################
            # Building final object
            ################################################################
            record = get_record_dict(
                f"{page['id']}-{uuid}",
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

            driver.back()

    driver.quit()

    return records
