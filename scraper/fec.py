import json
import re
import time

from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scraper.records import get_record_dict
from utils.readJson import get_address_data, strip_zip_code


def get_fec_data(dr, headless=False):
    print("Scraping data from lafresquedeleconomiecirculaire.com")

    options = FirefoxOptions()
    options.headless = headless

    driver = webdriver.Firefox(options=options, executable_path=dr)

    webSites = [
        {
            "url": "https://www.lafresquedeleconomiecirculaire.com/",
            "id": 300,
        },
    ]

    records = []

    for page in webSites:
        print(f"========================")
        driver.get(page["url"])
        driver.implicitly_wait(2)

        while True:
            print(f"Scrolling to the bottom...")
            try:
                time.sleep(2)
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            'button[data-hook="load-more-button"]',
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
                break

        driver.execute_script("window.scrollTo(0, 0);")

        ele = driver.find_elements(
            By.CSS_SELECTOR, 'li[data-hook="events-card"] div[data-hook="title"] a'
        )
        links = [e.get_attribute("href") for e in ele]

        for link in links:
            print(f"\n-> Processing {link} ...")
            driver.get(link)
            driver.implicitly_wait(3)
            time.sleep(5)

            ################################################################
            # Parse event id
            ################################################################
            # Define the regex pattern for UUIDs
            uuid = link.split("/event-details/")[-1]
            if not uuid:
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

            ################################################################
            # Parse start and end dates
            ################################################################
            try:
                date_info_el = driver.find_element(
                    by=By.CSS_SELECTOR,
                    value='p[data-hook="event-full-date"]',
                )
                event_time = date_info_el.text
            except NoSuchElementException:
                print("Rejecting record: no dates")
                continue

            month_mapping = {
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

            date_and_times = event_time.split(",")
            day_string = date_and_times[0].split(" ")
            if len(day_string) == 2:
                day = day_string[0]
                month_string = day_string[1]
                year = 2023
            elif len(day_string) == 3:
                day = day_string[0]
                month_string = day_string[1]
                year = day_string[2]
            else:
                print("Rejecting record: bad date format")
                continue

            times_and_timezone = date_and_times[1].split(" UTC")
            times = times_and_timezone[0].split(" – ")
            if len(times_and_timezone) >= 2:
                timezone = times_and_timezone[1]
                print(f"Rejecting record: different timezone")
                continue

            try:
                # Extract hours and minutes from time strings
                start_hour, start_minute = map(int, times[0].split(":"))
                end_hour, end_minute = map(int, times[1].split(":"))
            except:
                print(f"Rejecting record: bad date format")
                continue

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
            online = False
            try:
                online_el = driver.find_element(
                    By.CSS_SELECTOR, 'p[data-hook="event-full-location"]'
                )
                if (
                    "en ligne" in online_el.text.lower()
                    or "online" in online_el.text.lower()
                ):
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
                    By.CSS_SELECTOR, 'p[data-hook="event-full-location"]'
                )
                full_location = location_el.text

                if "," in full_location:
                    loc_arr = full_location.split(",")
                    if len(loc_arr) >= 5:
                        print(
                            f"Rejecting records: address is too long ({len(loc_arr)} parts)"
                        )
                        continue
                    elif len(loc_arr) >= 4:
                        if loc_arr[3].strip().lower() != "france":
                            print("rejecting record: not in France")
                            continue
                        location_name = loc_arr[0]
                        address = loc_arr[1]
                        city = loc_arr[2]
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

                if address == "" or city == "":
                    print("Rejecting record: empty address or city")
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
                    continue

            ################################################################
            # Description
            ################################################################
            description_el = driver.find_element(
                By.CSS_SELECTOR, "div#events-details-page-about-inner"
            )
            description = description_el.text

            ################################################################
            # Training?
            ################################################################
            training_list = ["formation", "briefing", "animateur"]
            training = any(w in title.lower() for w in training_list)

            ################################################################
            # Is it full?
            ################################################################
            sold_out = True
            try:
                sold_out_el = driver.find_element(
                    by=By.CSS_SELECTOR,
                    value='div[data-hook="event-sold-out"]',
                )
            except NoSuchElementException:
                sold_out = False

            ################################################################
            # Is it suited for kids?
            ################################################################
            kids = "junior" in title.lower()

            ################################################################
            # Parse tickets link
            ################################################################
            tickets_link = link

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
                tickets_link,
                description,
            )

            records.append(record)
            print(f"Successfully scraped {link}\n{json.dumps(record, indent=4)}")

    driver.quit()

    return records
