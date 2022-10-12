import json

from scraper.billetweb import get_billetweb_data
from scraper.eventbrite import get_eventbrite_data
from scraper.etl_proccess import etl

def main():  # pragma: no cover
    file = open('etl_config.json', 'r')
    file = json.loads(file.read())
    credentials = dict(file)

    #billetweb_records = get_billetweb_data(dr=credentials["chromedriver"])
    eventbrite_records = get_eventbrite_data(dr=credentials["chromedriver"])
    
    tot = billetweb_records + eventbrite_records
    df = pd.DataFrame(tot)

    df['flag_week'] = pd.to_datetime(
        df['end_date']) - pd.to_datetime(df['start_date'])

    df['location'] = df['location'].str.strip()
    df['location_name'] = df['location_name'].str.strip()
    df['location_address'] = df['location_address'].str.strip()
    df['location_city'] = df['location_city'].str.strip()

    df['flag_week'] = np.where(df['flag_week'] < '7 days',
                            'Less than 1 week', 'More than 1 week')
    df['scape_time'] = pd.to_datetime("now").strftime('%Y-%m-%d %H:%M:%S')

    etl(df)


    dt = datetime.datetime.now()
    insert_time = dt.strftime("%Y%m%d_%H%M%S ")

    with open(f'events_{insert_time}.json', 'w', encoding="UTF-8") as file:
        df.to_json(file, orient='records', force_ascii=False)



if __name__ == "__main__":  # pragma: no cover
    main()
