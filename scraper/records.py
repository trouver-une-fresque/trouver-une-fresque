from zoneinfo import ZoneInfo
from datetime import datetime


def get_record_dict(
    ids,
    title,
    start_datetime,
    end_datetime,
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
    event_link,
    tickets_link,
    description,
):
    origin_tz = ZoneInfo("Europe/Paris")

    return {
        "workshop_type": ids,
        "title": title,
        "start_date": start_datetime.replace(tzinfo=origin_tz).isoformat(),
        "end_date": end_datetime.replace(tzinfo=origin_tz).isoformat(),
        #'location': location,
        "full_location": full_location,
        "location_name": location_name,
        "address": address,
        "city": city,
        "department": department,
        "zip_code": zip_code,
        "latitude": latitude,
        "longitude": longitude,
        "online": online,
        "training": training,
        "sold_out": sold_out,
        "kids": kids,
        "source_link": event_link,
        "tickets_link": tickets_link,
        "description": description,
    }
