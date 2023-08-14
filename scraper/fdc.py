from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver


def get_fdc_data(dr, headless=False):
    print("Scraping data from fresqueduclimat.org\n\n")

    options = FirefoxOptions()
    options.headless = headless

    driver = webdriver.Firefox(options=options, executable_path=dr)

    webSites = [
        {
            "url": "https://fresqueduclimat.org/inscription-atelier/grand-public/",
            "id": 200,
        }
    ]

    records = []

    for page in webSites:
        print(f"\n========================")
        driver.get(page["url"])
        driver.implicitly_wait(5)
        while True:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "#events > section > div > div:nth-child(2) > div > div.organizer-profile__show-more.eds-l-pad-top-4.eds-align--center > button",
                        )
                    )
                )
                driver.execute_script("arguments[0].click();", element)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.implicitly_wait(2)
            except:
                break
            # ef = driver.find_elements(by=By.CSS_SELECTOR, value= '#events > section > div > div:nth-child(2) > div > div.organizer-profile__show-more.eds-l-pad-top-4.eds-align--center > button')
