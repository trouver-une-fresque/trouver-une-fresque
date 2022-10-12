import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

from scraper.eventbrite import ticket_api


def get_eventbrite_data(dr):

    print('\n\nThe script is extracting info from www.eventbrite.fr \n\n')

    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options, executable_path=dr)

    webSites = [
        {
            'url': 'https://www.eventbrite.fr/o/la-fresque-du-climat-18716137245',
            'id': 6
        },
        {
            'url': 'https://www.eventbrite.fr/o/2-tonnes-29470123869',
            'id': 7
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

        envents_link = list(
            filter(lambda n: 'https://www.eventbrite.fr/e/' in n, links))
        envents_ids = list(map(lambda n: n.split(
            '-')[-1].split('?')[0], envents_link))
        unique_ids = np.unique(envents_ids)
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
    # df = pd.DataFrame(records)
    # # df.to_csv('Poc.csv',sep =';',index=False)\
    # with open('POC_eventTribe.json', 'w', encoding="UTF-8") as file:
    #     df.to_json(file,orient='records', force_ascii=False)
    #     # ids = [link.split('-')[-1].sp]


# //*[@id="events"]/section/div/div[1]/div/div[1]/div[12]/div/article/div[1]/div[1]/div/div[1]/a
