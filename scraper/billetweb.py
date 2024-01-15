import re
import json
from datetime import timedelta

from dateutil.parser import parse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from db.records import get_record_dict
from utils.readJson import get_address_data, strip_zip_code


def get_billetweb_data(service, options):
    print("Scraping data from www.billetweb.fr")

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
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, page["iframe"])))
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        ele = driver.find_elements(By.CSS_SELECTOR, "a.naviguate")
        links = [e.get_attribute("href") for e in ele]

        for link in links:
            print(f"\n-> Processing {link} ...")
            driver.get(link)
            WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

            try:
                driver.find_element(By.ID, "more_info").click()
            except Exception:
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
            try:
                title_el = driver.find_element(
                    by=By.CSS_SELECTOR, value="#event_title > div.event_name"
                )
            except NoSuchElementException:
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
            try:
                time_el = driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="#event_title > div.event_start_time > span.text",
                )
            except NoSuchElementException:
                time_el = driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="#description_block > div.event_title > span > a > div.event_start_time",
                )
            event_time = time_el.text.lower()

            if match := re.match(r"(?P<date>.*)\sfrom\s(?P<start>.*)\sto\s(?P<end>.*)", event_time):
                # Thu Oct 19, 2023 from 01:00 PM to 02:00 PM
                event_start_datetime = parse(f"{match.group('date')} {match.group('start')}")
                event_end_datetime = parse(f"{match.group('date')} {match.group('end')}")
            elif match := re.match(r"(?P<start_date>.*)\sat\s(?P<start_time>.*)\sto\s(?P<end_date>.*)\sat\s(?P<end_time>.*)", event_time):
                # Thu Oct 19, 2023 at 01:00 PM to Sat Feb 24, 2024 at 02:00 PM
                event_start_datetime = parse(f"{match.group('start_date')} {match.group('start_time')}")
                event_end_datetime = parse(f"{match.group('end_date')} {match.group('end_time')}")
            elif match := re.match(r"(?P<date>.*)\sat\s(?P<time>.*)", event_time):
                # Thu Oct 19, 2023 at 01:00 PM
                event_start_datetime = parse(f"{match.group('date')} {match.group('time')}")
                event_end_datetime = event_start_datetime + timedelta(hours=3)
            else:
                print(f"Rejecting record: invalid dates: {event_time}")
                continue

            if event_end_datetime - event_start_datetime > timedelta(days=1):
                print(f"Rejecting record: event is too long: {event_time}")
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
                    try:
                        address_el = driver.find_element(
                            by=By.CSS_SELECTOR, value="div.location_summary"
                        )
                    except NoSuchElementException:
                        address_el = driver.find_element(
                            by=By.CSS_SELECTOR,
                            value="#page_block_location > div.location > div.location_info > div.address > a",
                        )
                except Exception:
                    print("Rejecting record: empty address")
                    continue

                full_location = address_el.text

                # Parse location fields
                if "," in full_location:
                    loc_arr = full_location.split(",")
                    if len(loc_arr) >= 5:
                        print(
                            f"Rejecting records: address is too long ({len(loc_arr)} parts): {full_location}"
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
                        "Rejecting record: error while parsing the national address API response"
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
            except Exception:
                print("Rejecting record: no description")
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
                WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it(
                        (By.CSS_SELECTOR, "#shop_block iframe")
                    )
                )
                WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
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
                driver.switch_to.parent_frame()

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
