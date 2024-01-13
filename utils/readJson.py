import re
import requests


def get_address_data(text_address):
    url = "https://api-adresse.data.gouv.fr/search"
    params = {"q": text_address, "limit": 1}
    response = requests.request("GET", url, params=params)
    data = response.json()

    try:
        housenumber = data["features"][0]["properties"]["housenumber"]
    except Exception:
        housenumber = ""
    try:
        postcode = data["features"][0]["properties"]["postcode"]
    except Exception:
        postcode = ""
    try:
        longitude = data["features"][0]["geometry"]["coordinates"][0]
    except Exception:
        longitude = ""
    try:
        latitude = data["features"][0]["geometry"]["coordinates"][1]
    except Exception:
        latitude = ""
    try:
        cod_dep = data["features"][0]["properties"]["context"].split(',')[0].strip()
    except Exception:
        cod_dep = ""

    return {
        "housenumber": housenumber,
        "postcode": postcode,
        "longitude": longitude,
        "latitude": latitude,
        "cod_dep": cod_dep,
    }


def strip_zip_code(text_address):
    zip_re = r"\b((0[1-9])|([1-8][0-9])|(9[0-8])|(2A)|(2B)) *([0-9]{3})?\b"
    zip_code = re.search(zip_re, text_address)
    if zip_code:
        text_address = text_address.replace(zip_code.group(0), "")
    return text_address.strip().title()
