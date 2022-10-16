import requests
import numpy as np
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from scraper.readJson import get_address_data


def ticket_api(ids):
    url = "https://www.eventbrite.fr/api/v3/destination/events/viewEvent"

    querystring = {"event_id": ids, "page_size": "1000",
                   "include_parent_events": "true"}

    payload = ""
    headers = {
        "cookie": "SS=AE3DLHSfQDO1YjBhawTa9YoWbFFw1nSGZQ; AS=fbc0e2ff-a732-45db-b007-9cae03360a78; SP=AGQgbbnSw8F--uDo-bLWSlW9ZTk1nEUfcmzZSTN6IwXtaOHA3m14Ajx39XrKzOSLlOy8dQJH0-HUB6oEXUJek0C8KCUbIrcum7cZUyz-yup9BUfGoFabzmqiozDziCDyBe-0rTGsYqwu_Ul8oXTQWzSFTG23_JTC3QWM6cAzpgX33A80tUnxaP_-NNeJvIUbuzLdHlCL_agzNJnh6xixZQhUi0OUAJTr8nPZizGGHYf7zHDUkgUCkUU; G=v%253D2%2526i%253Da3344c52-8935-49a1-b0a2-37ea4cbbbf78%2526a%253D1001%2526s%253D991368c96eed8f52ada6e8422c9eb77d883512d5",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9,sq;q=0.8,el;q=0.7,es;q=0.6",
        "Connection": "keep-alive",
        "Cookie": "G=v^%^3D2^%^26i^%^3De55de1db-f41a-4635-809c-238005512c0a^%^26a^%^3Dfd6^%^26s^%^3D2cdc32731cecf43e6a5aba2ebebdde1979191c1a; mgref=typeins; csrftoken=6807c3eae5d111ecaf04b30c0420ce5d; eblang=lo^%^3Dfr_FR^%^26la^%^3Dfr-fr; _ga=GA1.2.1270604210.1654544814; _gcl_au=1.1.379094521.1654544814; ebGAClientId=1270604210.1654544814; _scid=7b62bf4c-79bc-4bfc-a90f-c6508febfa36; _pin_unauth=dWlkPU16UmtaR1V3TVdRdFpHSm1OQzAwTmpZM0xUZzBabVF0WXpRMk9HRXlaR1ZsTUdabQ; _fbp=fb.1.1654544816226.1624514991; _sctr=1^|1654466400000; _gid=GA1.2.1114969091.1658262344; SS=AE3DLHSfQDO1YjBhawTa9YoWbFFw1nSGZQ; AS=fbc0e2ff-a732-45db-b007-9cae03360a78; SERVERID=djc76; _hp2_id.1404198904=^%^7B^%^22userId^%^22^%^3A^%^221243301556615404^%^22^%^2C^%^22pageviewId^%^22^%^3A^%^223283643756834549^%^22^%^2C^%^22sessionId^%^22^%^3A^%^221884191116488815^%^22^%^2C^%^22identity^%^22^%^3Anull^%^2C^%^22trackerVersion^%^22^%^3A^%^224.0^%^22^%^7D; _hp2_ses_props.1404198904=^%^7B^%^22ts^%^22^%^3A1658262346321^%^2C^%^22d^%^22^%^3A^%^22www.eventbrite.fr^%^22^%^2C^%^22h^%^22^%^3A^%^22^%^2Fo^%^2Fla-fresque-du-climat-18716137245^%^22^%^7D; _dd_s=rum=0&expire=1658263463901; SP=AGQgbbm690tGzlyrDyCpwnOatD-BJAlYNx3U6KJxTuwtiqFEPKWNuP6zcs47SwmWbutb6AzgkCZzRF_F91wKoXcsOllPAKidEz7b5MgwYXg63HW9qzTdlWlXdiBorsaXbo-UXIh6dYfc7JbGQRKPRqz3ZVradAqhhiP8qOFMdrWiLTgzQsIlKWnjGZGJqWZYC-LwscRipwO6EVksU6jGFYlZUjHibMZwjKGbHx4xcGyXSddART_umYY; _gat=1",
        "Referer": "https://www.eventbrite.fr/o/la-fresque-du-climat-18716137245",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "X-CSRFToken": "6807c3eae5d111ecaf04b30c0420ce5d",
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
    event_desc = data['summary']
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
        venue_id = data['primary_venue_id']
        venue_url = f"https://www.eventbriteapi.com/v3/venues/{venue_id}"
        headers['Authorization'] = 'Bearer FLTI22VGKT2FHC4B7ZA4'
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
        depart = ''

    res = {
        'title': title,
        'start_date': start_date,
        'start_time': start_time,
        'end_date': end_date,
        'end_time': end_time,
        'location': location_text,
        'location_name': location_name,
        'location_address': location_address,
        'location_city': location_city,
        'depart': depart,
        'postal_code': postal_code,
        'latitude': latitude,
        'longitude': longitude,
        "online": online,
        'training': training,
        'full': full,
        'original_source_link': tickets_url,
        'ticketing_platform_link': tickets_url,
        'event_desc': event_desc
    }

    return res


def get_eventbrite_data(dr):

    print('\n\nThe script is extracting info from www.eventbrite.fr \n\n')

    options = Options()
    options.headless = True

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
        driver.get(page['url'])
        time.sleep(5)
        while True:
            try:
                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#events > section > div > div:nth-child(2) > div > div.organizer-profile__show-more.eds-l-pad-top-4.eds-align--center > button')))
                driver.execute_script("arguments[0].click();", element)
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            except:
                break
            # ef = driver.find_elements(by=By.CSS_SELECTOR, value= '#events > section > div > div:nth-child(2) > div > div.organizer-profile__show-more.eds-l-pad-top-4.eds-align--center > button')

        ele = driver.find_elements('xpath', '//a[@href]')
        links = [e.get_attribute("href") for e in ele]

        events_link = list(
            filter(lambda n: 'https://www.eventbrite.fr/e/' in n, links))
        events_ids = list(map(lambda n: n.split(
            '-')[-1].split('?')[0], events_link))
        unique_ids = np.unique(events_ids)
        id_chunks = [unique_ids[x:x+20] for x in range(0, len(unique_ids), 20)]
        id_text = [','.join(chank) for chank in id_chunks]
        for ids in unique_ids:
            try:
                ticket_dic = ticket_api(ids)
                ticket_dic['page_id'] = page['id']
                records.append(ticket_dic)
                print(f'added event : {ids}')
            except:
                print(f'there was an error with event nr: {ids}')

    driver.quit()

    return records
