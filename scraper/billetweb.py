import numpy as np
import time
import pandas as pd
import requests
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from geopy.geocoders import Nominatim
from geopy import geocoders
from dateutil.parser import *

from scraper.readJson import get_address_data

def get_billetweb_data(dr):

    print('\n\nThe script is extracting info from www.billetweb.fr \n\n')

    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options, executable_path=dr)

    """
    {
        "url": "https://www.billetweb.fr/pro/fdnr",
        "iframe": 'event21569',
        "id": 4
    }
    """
    webSites = [
        {
            "url": "https://www.billetweb.fr/pro/billetteriefo",
            "iframe": 'event15247',
            "id": 1
        },
        {
            "url": "https://www.billetweb.fr/multi_event.php?user=82762",
            "iframe": 'event17309',
            "id": 2
        },
        {
            "url": "https://www.billetweb.fr/multi_event.php?user=84999",
            "iframe": 'eventu84999',
            "id": 3
        },
        {
            "url": "https://www.billetweb.fr/pro/fresqueagrialim",
            "iframe": 'event11421',
            "id": 3
        },

        {
            "url": "https://www.billetweb.fr/pro/fresquealimentation",
            "iframe": 'event11155',
            "id": 5
        }
    ]

    records = []
    count = 0

    for page in webSites:
        driver.get(page["url"])
        time.sleep(2)

        driver.switch_to.frame(page["iframe"])

        ele = driver.find_elements('xpath', '//a[@href]')

        links = [e.get_attribute("href") for e in ele]

        for link in links:
            if 'https://www.billetweb.fr/multi_event.php?&multi' not in link:

                driver.get(link)
                time.sleep(3)

                page_link = driver.find_element(
                    by=By.CSS_SELECTOR, value='#page_block_location > div > div.location_info > div.address > a')
                title_el = driver.find_element(
                    by=By.CSS_SELECTOR, value='#description_block > div.event_title.center > div.event_name.custom_font')
                title = title_el.text
                if 'cadeau' in title.lower():
                    break

                time_el = driver.find_element(
                    by=By.CSS_SELECTOR, value='#description_block > div.event_title.center > span > a > div')
                event_time = time_el.text
                event_arr = event_time.lower().split('from')
                if len(event_arr) > 1:
                    date_event = event_arr[0]
                    try:
                        time_split = event_arr[1].split('to')
                        start_time = time_split[0]
                        end_time = time_split[1]
                    except:
                        time_split = event_arr[1].split("at ", '')
                        start_time = time_split[0]
                        end_time = ''

                    event_start_time = f'{date_event}, {start_time}'
                    event_end_time = f'{date_event}, {end_time}'
                else:
                    try:
                        event_arr = event_time.lower().split('to')
                        start_time = event_arr[0]
                        end_time = event_arr[1]
                    except:
                        event_arr = event_time.lower().split('at')
                        date_event = event_arr[0]
                        try:
                            start_time = event_arr[1]
                        except:
                            start_time = ''
                        end_time = ''

                    event_start_time = f'{start_time}'
                    event_end_time = f'{end_time}'

                if page_link.get_attribute("href") == "http://maps.google.fr/maps?q=":
                    try:
                        page_link = driver.find_element(
                            by=By.CSS_SELECTOR, value='#description_block > div.event_title.center > div.event_name.custom_font > a.action_button.secondary.virtual.active')
                        location = page_link.text
                        location_text = page_link.text
                    except:
                        location_text = 'Online Event'
                    if 'EN LIGNE' in title.upper():
                        location_text = 'Online Event'
                    depart = ''
                    postal_code = ''
                    longitude = ''
                    lattitude = ''
                else:
                    location = page_link.get_attribute("href")
                    location_text = page_link.text
                    address_dict = get_address_data(location_text)

                    try:
                        depart = address_dict['cod_dep']
                    except:
                        depart = ''
                    try:
                        longitude = address_dict['longitude']
                    except:
                        longitude = ''
                    try:
                        lattitude = address_dict['lattitude']
                    except:
                        lattitude = ''
                    try:
                        postal_code = address_dict['postcode']
                    except:
                        postal_code = ''

                try:
                    even_el = driver.find_element(
                        by=By.CSS_SELECTOR, value='#description > div:nth-child(3)')
                except:
                    try:
                        even_el = driver.find_element(
                            by=By.CSS_SELECTOR, value='#description > div > div > div')
                    except:
                        even_el = driver.find_element(
                            by=By.CSS_SELECTOR, value='#description_block > div.ckeditor_block')

                event_desc = even_el.text
                trainning_list = ["formation", "briefing", "animateur"]
                check_tr = 0
                for w in trainning_list:
                    if w in title.lower():
                        check_tr = + 1
                if check_tr > 0:
                    training = 'True'
                else:
                    training = 'False'

                if 'online' in title.lower() or 'en ligne' in title.lower():
                    online = 'True'
                else:
                    online = 'False'
                if ',' in location_text:
                    loc_arr = location_text.split(',')
                    if len(loc_arr) >= 3:
                        if loc_arr[2] == 'France':
                            location_name = ''
                            location_address = loc_arr[0]
                            location_city = loc_arr[1]
                        else:
                            location_name = loc_arr[0]
                            location_address = loc_arr[1]
                            location_city = loc_arr[2]

                    elif len(loc_arr) >= 2:
                        location_name = ''
                        location_address = loc_arr[0]
                        location_city = loc_arr[1]
                else:
                    location_name = ''
                    location_address = ''
                    location_city = ''

                    count += 1
                    # print(f"The are {count} events ok with criteria")
                    # print(f"location_name: {location_name}, location_address:{location_address},location_city: {location_city}")

                try:
                    start_datetime = parse(event_start_time)
                except:
                    start_datetime = parse(event_time)

                # print(start_datetime)

                start_date = start_datetime.strftime('%Y-%m-%d')
                start_time = start_datetime.strftime('%H:%M:%S')

                try:
                    end_datetime = parse(event_end_time)
                    end_date = end_datetime.strftime('%Y-%m-%d')
                    end_time = end_datetime.strftime('%H:%M:%S')
                except:
                    end_date = ''
                    end_time = ''

                # print(event_start_time)

                record = {
                    'page_id': page["id"],
                    'title': title,
                    'start_date': start_date,
                    'start_time': start_time,
                    'end_date': end_date,
                    'end_time': end_time,
                    'location': location,
                    'location_name': location_name,
                    'location_address': location_address,
                    'location_city': location_city,
                    'depart': depart,
                    'postal_code': postal_code,
                    'latitude': lattitude,
                    'longitude': longitude,
                    'online': online,
                    'training': training,
                    'original_source_link': link,
                    'ticketing_platform_link': link,
                    'event_desc': event_desc
                }
                records.append(record)

                print(f"\nJust scraped {link}\n\t{record}")
    
    driver.quit()

    return records
