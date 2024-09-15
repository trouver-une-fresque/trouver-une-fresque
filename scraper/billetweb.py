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
from utils.errors import FreskError
from utils.location import get_address


def get_billetweb_data(service, options):
    print("Scraping data from www.billetweb.fr")

    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 10)

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
            "iframe": "event38362",
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
        {
            # Puzzle Climat
            "url": "https://www.billetweb.fr/multi_event.php?user=121600",
            "iframe": "event21038",
            "id": 16,
        },
        {
            # Fresque de la Finance
            "url": "https://www.billetweb.fr/pro/fresquedelafinance",
            "iframe": "event34683",
            "id": 17,
        },
        {
            # Fresque de la RSE
            "url": "https://www.billetweb.fr/pro/fresque",
            "iframe": "event35904",
            "id": 18,
        },
    ]

    records = []

    for page in webSites:
        print(f"==================\nProcessing page {page}")
        driver.get(page["url"])
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, page["iframe"])))
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        ele = driver.find_elements(By.CSS_SELECTOR, "a.naviguate")
        links = [e.get_attribute("href") for e in ele]

        for link in links:
            print(f"------------------\nProcessing event {link}")
            driver.get(link)
            wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # Useful for different workshops sharing same event link
            if "filter" in page:
                if page["filter"] not in link:
                    print("Rejecting filter: expected filter keyword not present in current link")
                    continue

            # Description
            try:
                driver.find_element(By.ID, "more_info").click()
            except Exception:
                pass  # normal case if description is without more info

            try:
                description = driver.find_element(by=By.CSS_SELECTOR, value="#description").text
            except Exception:
                print("Rejecting record: no description")
                continue

            # Parse event id
            event_id = re.search(r"/([^/]+?)&", link).group(1)
            if not event_id:
                print("Rejecting record: event_id not found")
                continue

            # Parse main title
            try:
                main_title = driver.find_element(
                    by=By.CSS_SELECTOR, value="#event_title > div.event_name"
                ).text
            except NoSuchElementException:
                main_title = driver.find_element(
                    by=By.CSS_SELECTOR,
                    value="#description_block > div.event_title > div.event_name",
                ).text

            # Location data
            try:
                try:
                    main_full_location = driver.find_element(
                        by=By.CSS_SELECTOR, value="div.location_summary"
                    ).text
                except NoSuchElementException:
                    main_full_location = driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="#page_block_location > div.location > div.location_info > div.address > a",
                    ).text
            except Exception:
                main_full_location = ""

            event_info = []

            # Retrieve sessions if exist
            wait.until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "#shop_block iframe"))
            )
            wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            back_links = driver.find_elements(By.CSS_SELECTOR, ".back_header_link.summarizable")
            if back_links:
                # Case of Multi-time with only one date, we arrive directly to Basket, so get back to sessions
                driver.get(back_links[0].get_attribute("href"))
                wait.until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
            sessions = driver.find_elements(By.CSS_SELECTOR, "a.sesssion_href")
            sessions_links = [
                s.get_attribute("href") for s in sessions
            ]  # No sessions for Mono-time
            driver.switch_to.parent_frame()

            ################################################################
            # Multi-time management
            ################################################################
            for sessions_link in sessions_links:
                driver.get(sessions_link)
                wait.until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                context = driver.find_element(By.CSS_SELECTOR, "#context_title").text

                # Parse title, dates, location
                if match := re.match(
                    r"\s*((?P<title>.*) : )?(?P<event_time>.*)(\n\s*(?P<full_location>.*))?",
                    context,
                ):
                    if not match.group("title"):
                        sub_title = main_title
                    elif "atelier" in match.group("title").lower():
                        sub_title = match.group("title")
                    else:
                        sub_title = main_title + " - " + match.group("title")

                    event_time = match.group("event_time")
                    sub_full_location = (
                        match.group("full_location")
                        if match.group("full_location")
                        else main_full_location
                    )
                else:
                    raise

                # Is it full?
                try:
                    # The presence of div.block indicates that the event is sold out,
                    # except if the text below is displayed.
                    empty = driver.find_element(By.CSS_SELECTOR, "div.block")
                    sold_out = (
                        "inscriptions uniquement" not in empty.text.lower()
                        and "inscription uniquement" not in empty.text.lower()
                        and "inscriptions via" not in empty.text.lower()
                        and "inscription via" not in empty.text.lower()
                    )
                except NoSuchElementException:
                    sold_out = False

                # Parse session id
                session_id = re.search(r"&session=(\d+)", sessions_link).group(1)
                uuid = f"{event_id}-{session_id}"

                event_info.append(
                    [sub_title, event_time, sub_full_location, sold_out, sessions_link, uuid]
                )

            ################################################################
            # Mono-time management
            ################################################################
            if not sessions_links:
                # Parse start and end dates
                try:
                    event_time = driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="#event_title > div.event_start_time > span.text",
                    ).text
                except NoSuchElementException:
                    event_time = driver.find_element(
                        by=By.CSS_SELECTOR,
                        value="#description_block > div.event_title > span > a > div.event_start_time",
                    ).text

                # Is it full?
                try:
                    wait.until(
                        EC.frame_to_be_available_and_switch_to_it(
                            (By.CSS_SELECTOR, "#shop_block iframe")
                        )
                    )
                    wait.until(
                        lambda driver: driver.execute_script("return document.readyState")
                        == "complete"
                    )

                    # The presence of div.block indicates that the event is sold out,
                    # except if the text below is displayed.
                    empty = driver.find_element(By.CSS_SELECTOR, "div.block")
                    sold_out = (
                        "inscriptions uniquement" not in empty.text.lower()
                        and "inscription uniquement" not in empty.text.lower()
                        and "inscriptions via" not in empty.text.lower()
                        and "inscription via" not in empty.text.lower()
                    )
                except NoSuchElementException:
                    sold_out = False
                finally:
                    driver.switch_to.parent_frame()

                event_info.append(
                    [main_title, event_time, main_full_location, sold_out, link, event_id]
                )

            ################################################################
            # Session loop
            ################################################################
            for index, (title, event_time, full_location, sold_out, ticket_link, uuid) in enumerate(
                event_info
            ):
                print(f"\n-> Processing session {index+1}/{len(event_info)} {ticket_link} ...")
                if "cadeau" in title.lower() or " don" in title.lower():
                    print("Rejecting record: gift card")
                    continue

                if match := re.match(
                    r"(?P<date>.*)\sfrom\s(?P<start>.*)\sto\s(?P<end>.*)", event_time
                ):
                    # Thu Oct 19, 2023 from 01:00 PM to 02:00 PM
                    event_start_datetime = parse(f"{match.group('date')} {match.group('start')}")
                    event_end_datetime = parse(f"{match.group('date')} {match.group('end')}")
                elif match := re.match(
                    r"(?P<start_date>.*)\sat\s(?P<start_time>.*)\sto\s(?P<end_date>.*)\sat\s(?P<end_time>.*)",
                    event_time,
                ):
                    # Thu Oct 19, 2023 at 01:00 PM to Sat Feb 24, 2024 at 02:00 PM
                    event_start_datetime = parse(
                        f"{match.group('start_date')} {match.group('start_time')}"
                    )
                    event_end_datetime = parse(
                        f"{match.group('end_date')} {match.group('end_time')}"
                    )
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

                # Is it an online event?
                online_list = ["online", "en ligne", "distanciel"]
                online = any(w in title.lower() for w in online_list) or any(
                    w in full_location.lower() for w in online_list
                )
                title = title.replace(" Online event", "")  # Button added by billetweb

                ################################################################
                # Location data
                ################################################################
                location_name = address = city = department = longitude = latitude = zip_code = ""
                if not online:
                    try:
                        address_dict = get_address(full_location)
                        (
                            location_name,
                            address,
                            city,
                            department,
                            zip_code,
                            latitude,
                            longitude,
                        ) = address_dict.values()
                    except FreskError as error:
                        print(f"Rejecting record: {error}.")
                        continue

                # Training?
                training_list = ["formation", "briefing", "animateur", "permanence", "training"]
                training = any(w in title.lower() for w in training_list)

                # Is it suited for kids?
                kids_list = ["kids", "junior", "jeunes"]
                kids = (
                    any(w in title.lower() for w in kids_list) and not training
                )  # Case of trainings for kids

                # Building final object
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
                    ticket_link,
                    description,
                )
                records.append(record)
                print(f"Successfully scraped:\n{json.dumps(record, indent=4)}")

    driver.quit()

    return records
