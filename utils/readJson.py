import csv
import re
import requests

from io import StringIO


def get_french_address(location, address, postcode, city):
    full_address = f"{address} {postcode} {city}"
    url = "https://api-adresse.data.gouv.fr/search"
    params = {"q": full_address, "limit": 1}
    response = requests.get(url, params=params)
    if data:= response.json():
        return {
            "location_name": location,
            "address": data["features"][0]["properties"]["name"],
            "city": data["features"][0]["properties"]["city"],
            "departement": data["features"][0]["properties"]["context"].split(',')[0].strip(),
            "zip_code": data["features"][0]["properties"]["postcode"],
            "latitude": data["features"][0]["geometry"]["coordinates"][1],
            "longitude": data["features"][0]["geometry"]["coordinates"][0],
        }
    return {
        "location_name": "",
        "address": "",
        "city": "",
        "department": "",
        "zip_code": "",
        "latitude": "",
        "longitude": "",
    }


def get_default_address(full_address):
    full_address = full_address.replace(",", " ").replace('  ', ' ').strip()  # for csv
    words = full_address.split()

    # create a list of address removing one word for each line until three words minimum
    if lines := "\n".join(' '.join(words[i:]) for i in range(len(words)) if len(words[i:]) >= 3):
        url = "https://api-adresse.data.gouv.fr/search/csv/"
        files = {'data': StringIO("query\n" + lines)}
        response = requests.post(url, files=files)
        if data_list := list(csv.DictReader(StringIO(response.text))):
            data_list = list(map(lambda x: {**x, 'result_score': float(x['result_score']) if x['result_score'] != '' else 0.0}, data_list))
            max_data = max(data_list, key=lambda x:x['result_score'])
            if max_data["result_score"] > 0.5:  # keep only good results
                return {
                    "location_name": full_address.removesuffix(max_data["query"]).rstrip("- "),
                    "address": max_data["result_name"],
                    "city": max_data["result_city"],
                    "department": max_data["result_context"].split(',')[0].strip(),
                    "zip_code": max_data["result_postcode"],
                    "latitude": float(max_data["latitude"]),
                    "longitude": float(max_data["longitude"]),
                }
    return {
        "location_name": "",
        "address": "",
        "city": "",
        "department": "",
        "zip_code": "",
        "latitude": "",
        "longitude": "",
    }

def get_address(full_location):
    if match := re.match(r"(?P<location>.+), (?P<street>[^,]+), ((?P<postcode>\d{2} ?\d{3}) )?(?P<city>[^,]+), France$", full_location):
        postcode = match.group('postcode') if match.group('postcode') else ''
        return get_french_address(match.group("location"), match.group("street"), postcode, match.group("city"))
    elif match := re.match(r"(?P<street>[^,]+), ((?P<postcode>\d{5}) )?(?P<city>[^,]+), France$", full_location):
        postcode = match.group('postcode') if match.group('postcode') else ''
        return get_french_address("", match.group("street"), postcode, match.group("city"))
    elif match := re.match(r"(?P<location>.+), (?P<street>[^,]+),? (?P<postcode>\d{2} ?\d{3}) (?P<city>[^,]+)$", full_location):
        return get_french_address(match.group("location"), match.group("street"), match.group('postcode'), match.group("city"))
    elif match := re.match(r"(?P<street>[^,]+),? (?P<postcode>\d{5}) (?P<city>[^,]+)$", full_location):
        return get_french_address("", match.group("street"), match.group('postcode'), match.group("city"))
    return get_default_address(full_location)


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
