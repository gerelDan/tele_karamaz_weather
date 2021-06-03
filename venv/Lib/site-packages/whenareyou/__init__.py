import os
from functools import lru_cache
from dateutil import tz

import requests
import csv
from urllib.parse import quote_plus
from pytz import timezone
from tzwhere import tzwhere


LONG_LAT_URL = ('https://maps.googleapis.com/maps/api/geocode/json?address={0}'
                '&sensor=false')

airports_csv_path = os.path.join(os.path.dirname(__file__), 'airports.csv')

airports_dict = {}

with open(airports_csv_path) as csvfile:
    airports_reader = csv.DictReader(
        csvfile,
        fieldnames=['id', 'name', 'city', 'country', 'iata', 'icao', 'lat',
                    'lng', 'alt', 'tz', 'dst', 'tz_olson'],
        restkey='info')
    for row in airports_reader:
        airports_dict[row['iata']] = row


tzw = tzwhere.tzwhere()


@lru_cache(None)
def cached_json_get(url):
    """
    Makes a get to that URL and caches it. Simple right? Oh it also returns the
    JSON as a dict for you already!
    """
    return requests.get(url).json()


def get_tz(lat, lng):
    tzinfo = tzw.tzNameAt(lat, lng)
    if tzinfo:
        return timezone(tzinfo)
    else:
        return None


def whenareyou(address):
    latlong = cached_json_get(
        LONG_LAT_URL.format(quote_plus(address))
    )['results'][0]['geometry']['location']

    return get_tz(latlong['lat'], latlong['lng'])


def whenareyou_apt(airport):
    if not airports_dict[airport]['tz_olson']=='\\N':
        return timezone(airports_dict[airport]['tz_olson'])
    else:
        tzinfo = get_tz(float(airports_dict[airport]['lat']),
                        float(airports_dict[airport]['lng']))
        if tzinfo:
            return tzinfo
        else:
            tot_offset = float(airports_dict[airport]['tz'])*3600
            return tz.tzoffset(airports_dict[airport]['name'] + ' ' +
                               airports_dict[airport]['city'], tot_offset)



if __name__ == '__main__':
    main()
