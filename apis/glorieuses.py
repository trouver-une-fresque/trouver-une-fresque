import json
import requests

from datetime import datetime

from db.records import get_record_dict
from utils.readJson import get_address_data, strip_zip_code


def get_glorieuses_data():
    print("Getting data from Glorieuses API")

    url = "https://hook.eu1.make.com/koqwhb0igq5air3aysx58rsjeld1uacl"
    type_id = 600

    json_records = []
    records = []

    try:
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            json_records = response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

    for json_record in json_records:
        ################################################################
        # Get event id
        ################################################################
        event_id = json_record["RECORD_ID()"]

        ################################################################
        # Get event title
        ################################################################
        title = json_record["Label event"]

        ################################################################
        # Parse start and end dates
        ################################################################
        event_start_time = json_record["Date"]

        try:
            # Convert time strings to datetime objects
            event_start_datetime = datetime.strptime(
                event_start_time, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        except Exception as e:
            print(f"Rejecting record: bad date format {e}")
            continue

        event_end_time = json_record["Date fin"]

        try:
            # Convert time strings to datetime objects
            event_end_datetime = datetime.strptime(
                event_end_time, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        except Exception as e:
            print(f"Rejecting record: bad date format {e}")
            continue

        ###########################################################
        # Is it an online event?
        ################################################################
        online = "en ligne" in json_record["Format"].lower()

        ################################################################
        # Location data
        ################################################################
        full_location = ""
        location_name = ""
        address = ""
        city = ""
        department = ""
        longitude = ""
        latitude = ""
        zip_code = ""

        if not online:
            address = json_record["Adresse"]
            city = json_record["Ville"]

            ############################################################
            # Localisation sanitizer
            ############################################################
            search_query = f"{address}, {city}, France"
            address_dict = get_address_data(search_query)

            department = address_dict.get("cod_dep", "")
            longitude = address_dict.get("longitude", "")
            latitude = address_dict.get("latitude", "")
            zip_code = address_dict.get("postcode", "")

            if department == "":
                print("Rejecting record: no result from the national address API")
                continue

        ################################################################
        # Description
        ################################################################
        description = json_record["Label event"]

        ################################################################
        # Training?
        ################################################################
        training_list = ["formation", "briefing", "animateur"]
        training = any(w in json_record["Type"].lower() for w in training_list)

        ################################################################
        # Is it full?
        ################################################################
        sold_out = False

        ################################################################
        # Is it suited for kids?
        ################################################################
        kids = False

        ################################################################
        # Parse tickets link
        ################################################################
        tickets_link = json_record["Lien billeterie"]

        ################################################################
        # Building final object
        ################################################################
        record = get_record_dict(
            f"{type_id}-{event_id}",
            type_id,
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
            "api",  # API
            tickets_link,
            description,
        )

        records.append(record)
        print(f"Successfully API record\n{json.dumps(record, indent=4)}")

    return records
