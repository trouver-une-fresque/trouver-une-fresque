import requests
import numpy as np
import pandas as pd
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from scraper.records import get_record_dict
from utils.readJson import get_address_data


def ticket_api(page_id, eventbrite_id, link):
    url = "https://www.eventbrite.fr/api/v3/destination/events/viewEvent"

    querystring = {"event_id": eventbrite_id, "page_size": "1000",
                   "include_parent_events": "true"}

    payload = ""
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9,sq;q=0.8,el;q=0.7,es;q=0.6",
        "Connection": "keep-alive",
        "Referer": "https://www.eventbrite.fr/o/la-fresque-du-climat-18716137245",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": "^\^.Not/A",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "^\^Windows^^"
    }

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring)
    data = response.json()
    field_training = ['formation', 'training']

    start_date = data['start_date']
    start_time = data['start_time']
    end_date = data['end_date']
    end_time = data['end_time']
    title = data['name']
    description = data['summary']
    tickets_url = data['tickets_url']
    online = str(data['is_online_event'])
    if field_training[0] in title.lower() or field_training[1] in title.lower():
        training = 'True'
    else:
        training = 'False'

    if 'complet' in title.lower():
        full = 'True'
    else:
        full = 'False'

    if online == 'False':
        file = open('config.json', 'r')
        file = json.loads(file.read())
        credentials = dict(file)
        headers['Authorization'] = credentials["eventbrite_auth"]

        venue_id = data['primary_venue_id']
        venue_url = f"https://www.eventbriteapi.com/v3/venues/{venue_id}"
        venue_response = requests.request(
            "GET", url=venue_url, headers=headers)
        venue_data = venue_response.json()
        latitude = venue_data['latitude']
        longitude = venue_data['longitude']
        postal_code = venue_data['address']['postal_code']
        location_text = venue_data['address']['localized_address_display']
        address_dict = get_address_data(location_text)
        try:
            depart = address_dict['cod_dep']
        except:
            depart = ''
        if ',' in location_text:
            loc_arr = location_text.split(',')
            if len(loc_arr) == 2:
                location_name = ''
                location_address = loc_arr[0]
                location_city = loc_arr[1]
            elif len(loc_arr) == 3:
                location_name = loc_arr[0]
                location_address = ''
                location_city = loc_arr[1]
            elif len(loc_arr) > 3:
                location_name = loc_arr[0]
                location_address = loc_arr[1]
                location_city = loc_arr[-2]
        else:
            location_name = ''
            location_address = ''
            location_city = ''
    else:
        latitude = ''
        longitude = ''
        postal_code = ''
        location_text = ''
        location_name = ''
        location_address = ''
        location_city = ''
        depart = ''
    location_name = location_name.strip()
    location_address = location_address.strip()
    location_city = location_city.strip().title()

    res = get_record_dict(page_id, title, start_date, start_time,
        end_date, end_time, location_text, location_name,
        location_address, location_city, depart, postal_code,
        latitude, longitude, online, training, full, False, link, tickets_url, description)

    return res


def get_eventbrite_data(dr, headless=False):
    print('Scraping data from www.eventbrite.fr\n\n')

    options = Options()
    options.headless = headless

    driver = webdriver.Chrome(options=options, executable_path=dr)

    webSites = [
        {
            # Fresque du Climat
            'url': 'https://www.eventbrite.fr/o/la-fresque-du-climat-18716137245',
            'id': 100
        },
        {
            # 2tonnes
            'url': 'https://www.eventbrite.fr/o/2-tonnes-29470123869',
            'id': 101
        }
    ]

    records = []

    for page in webSites:
        print(f"\n==================\nProcessing page {page}")
        driver.get(page['url'])
        driver.implicitly_wait(5)
        while True:
            try:
                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#events > section > div > div:nth-child(2) > div > div.organizer-profile__show-more.eds-l-pad-top-4.eds-align--center > button')))
                driver.execute_script("arguments[0].click();", element)
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                driver.implicitly_wait(2)
            except:
                break
            # ef = driver.find_elements(by=By.CSS_SELECTOR, value= '#events > section > div > div:nth-child(2) > div > div.organizer-profile__show-more.eds-l-pad-top-4.eds-align--center > button')

        ele = driver.find_elements('xpath', '//a[@href]')
        links = [e.get_attribute("href") for e in ele]

        events_link = list(
            filter(lambda n: 'https://www.eventbrite.fr/e/' in n, links)
        )
        events_ids = list(
            map(lambda n: int(n.split('-')[-1].split('?')[0]), events_link)
        )
        unique_ids, unique_index = np.unique(events_ids, return_index=True)
        unique_links = np.array(events_link)[unique_index]

        for eventbrite_id, link in zip(unique_ids, unique_links):
            try:
                print(f"-> Processing {link}...")
                ticket_dic = ticket_api(page["id"], eventbrite_id, link )
                records.append(ticket_dic)
                print(f'Successfully scraped {link}\n{json.dumps(ticket_dic, indent=4)}')
            except Exception as e:
                print(f'Rejecting record id={eventbrite_id}: {e}')

    driver.quit()

    return records
