import requests

# postcode =  "75015"


def departement_code(postcode):

    try:

        re = requests.get(
            url="https://raw.githubusercontent.com/CovidTrackerFr/vitemadose/main/data/input/codepostal_to_insee.json")

        data_from_link = dict(re.json())

        insee = data_from_link[postcode]

        insee_code = insee['insee']

        re2 = requests.get(
            url="https://raw.githubusercontent.com/CovidTrackerFr/vitemadose/main/data/input/insee_to_codepostal_and_code_departement.json")

        dep_data_from_link = dict(re2.json())

        dep_dict = dep_data_from_link[insee_code]

        departement_code = dep_dict['departement']

        return departement_code
    except:
        return ''

# lis = [item for item in data_from_link.values() if item['nom'] != None]
# list = [item["departement"] for item in lis if item['code postal'] == postcode ]
# if len(list) >0:
#     # return list[0]
# else :
#     # return ''


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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }

    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring)
    data = response.json()
    try:
        housenumber = data['features'][0]['properties']['housenumber']
    except:
        housenumber = ''
    try:
        postcode = data['features'][0]['properties']['postcode']
    except:
        postcode = ''
    try:
        longitude = data['features'][0]['geometry']['coordinates'][0]
    except:
        longitude = ''
    try:
        lattitude = data['features'][0]['geometry']['coordinates'][1]
    except:
        lattitude = ''
    cod_dep = departement_code(postcode)

    results = {

        'housenumber': housenumber,
        'postcode': postcode,
        'longitude': longitude,
        'lattitude': lattitude,
        'cod_dep': cod_dep
    }

    return results
