import pandas as pd
import requests
from datetime import datetime
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__file__)

logger.info("Starting extraction")
parsed_date = datetime.today().date().strftime('%Y%m%d')
logger.info(f"Date: {parsed_date}")
filename = f'Fire_incidents_{parsed_date}.csv'

logger.info("Downloading from Source")
raw_data = requests.get(f'https://data.sfgov.org/api/views/wr8u-xric/rows.csv?fourfour=wr8u-xric&date={parsed_date}&accessType=DOWNLOAD')
logger.info("Downloaded! Writing to file")
open(f"data/raw/{filename}", 'w+').write(raw_data.text)
logger.info(f"File '{filename}' generated!")

logger.info("Preparing to insert it to database")

dtypes = {
    "incident_number": "int64",
    "exposure_number": "int64",
    "id": "int64",
    "address": "string",
    "call_number": "string",
    "city": "string",
    "zipcode": "string",
    "battalion": "string",
    "station_area": "string",
    "box": "string",
    "suppression_units": "int64",
    "suppression_personnel": "int64",
    "ems_units": "int64",
    "ems_personnel": "int64",
    "other_units": "int64",
    "other_personnel": "int64",
    "fire_fatalities": "int64",
    "fire_injuries": "int64",
    "civilian_fatalities": "int64",
    "civilian_injuries": "int64",
    "number_of_alarms": "int64",
    "primary_situation": "string",
    "mutual_aid": "string",
    "action_taken_primary": "string",
    "action_taken_secondary": "string",
    "property_use": "string",
    "no_flame_spread": "string",
    "supervisor_district": "string",
    "neighborhood_district": "string"
}

parse_dates = [
    "incident_date",
    "alarm_dttm",
    "arrival_dttm",
    "close_dttm",
    "data_as_of",
    "data_loaded_at"
]

df = pd.read_csv(f'data/raw/{filename}', low_memory=False)
df.columns = [col.lower().replace(' ', '_') for col in df.columns]

df = df.astype({**dtypes})
df[parse_dates] = df[parse_dates].apply(pd.to_datetime, errors='coerce')

df = df.drop(columns=['point'])

df.to_sql('fire_incidents', "postgresql+psycopg2://ntdUser:ntdPass@localhost:6543/ntd", if_exists="append", index=False)
logger.info("Done!")
