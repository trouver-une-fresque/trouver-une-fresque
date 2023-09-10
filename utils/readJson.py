import re
import requests


def department_code(postcode):
    try:
        re = requests.get(
            url="https://raw.githubusercontent.com/trouver-une-fresque/trouver-une-fresque/main/data/codepostal_to_insee.json"
        )

        data_from_link = dict(re.json())
        insee = data_from_link[postcode]
        insee_code = insee["insee"]

        re2 = requests.get(
            url="https://raw.githubusercontent.com/trouver-une-fresque/trouver-une-fresque/main/data/insee_to_codepostal_and_code_departement.json"
        )

        dep_data_from_link = dict(re2.json())
        dep_dict = dep_data_from_link[insee_code]
        department_code = dep_dict["departement"]

        return department_code
    except Exception as error:
        print(f"An error occurred while getting the department code:", error)
        return ""


def get_address_data(text_address):
    url = "https://api-adresse.data.gouv.fr/search"

    querystring = {"q": text_address, "limit": "7"}

    payload = ""
    headers = {
        "authority": "api-adresse.data.gouv.fr",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,sq;q=0.8,el;q=0.7,es;q=0.6",
        "origin": "https://adresse.data.gouv.fr",
        "referer": "https://adresse.data.gouv.fr/",
        "sec-ch-ua": "^\^.Not/A",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "^\^Windows^^",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring
    )
    data = response.json()
    try:
        housenumber = data["features"][0]["properties"]["housenumber"]
    except:
        housenumber = ""
    try:
        postcode = data["features"][0]["properties"]["postcode"]
    except:
        postcode = ""
    try:
        longitude = data["features"][0]["geometry"]["coordinates"][0]
    except:
        longitude = ""
    try:
        latitude = data["features"][0]["geometry"]["coordinates"][1]
    except:
        latitude = ""
    cod_dep = department_code(postcode)

    results = {
        "housenumber": housenumber,
        "postcode": postcode,
        "longitude": longitude,
        "latitude": latitude,
        "cod_dep": cod_dep,
    }

    return results


def strip_zip_code(text_address):
    zip_re = r"\b((0[1-9])|([1-8][0-9])|(9[0-8])|(2A)|(2B)) *([0-9]{3})?\b"
    zip_code = re.search(zip_re, text_address)
    if zip_code:
        text_address = text_address.replace(zip_code.group(0), "")
    return text_address.strip().title()
