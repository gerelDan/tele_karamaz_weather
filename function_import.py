# import sys

# sys.path.insert(0, '/usr/lib/python3.10/site-packages')
# sys.path.insert(1, ' /usr/local/lib/python3.8/dist-packages')  # /usr/lib/python3.8/site-packages')
from geopy import geocoders
import requests as req
from os import environ
from googlesearcher import *
import json
from datetime import datetime  # , timedelta
import asyncio
import aiohttp
# from tokensy import *


async def code_location(latitude: str, longitude: str, token_accu: str):
    async with aiohttp.ClientSession() as session:
        url_location_key = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=' \
                           f'{token_accu}&q={latitude},{longitude}&language=ru'
        async with session.get(url_location_key, headers={"APIKey": token_accu}, ) as resp_loc:
            body = await resp_loc.text()
        json_data = json.loads(body)
        try:
            code = json_data['Key']
            print('code location is done')
        except KeyError:
            print('Error in code location Key Error')
            code = 'Moscow'
        return code


async def weather(cod_loc: str, token_accu: str):
    url_weather = f'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{cod_loc}?' \
                  f'apikey={token_accu}&language=ru&metric=True'

    async with aiohttp.ClientSession() as session:
        async with session.get(url_weather, headers={"APIKey": token_accu}) as response:
            body = await response.text()
        json_data = json.loads(body)
        dict_weather = dict()
        time = 'now'
        dict_weather[time] = {'temp': json_data[0]['Temperature']['Value'], 'sky': json_data[0]['IconPhrase']}
        for i in range(3, len(json_data), 3):
            time = f'after {i} h'
            dict_weather[time] = {'temp': json_data[i]['Temperature']['Value'],
                                  'sky': json_data[i]['IconPhrase'].lower()}
        print('accuweather is done')
        return dict_weather


def geo_pos(city: str):
    geolocator = geocoders.Nominatim(user_agent="telebot")
    latitude = str(geolocator.geocode(city).latitude)
    longitude = str(geolocator.geocode(city).longitude)
    print('geoposition is done')
    return latitude, longitude


async def open_weather(lat, lon, open_token):
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}' \
          f'&lang=ru&appid={open_token}&units=metric&cnt=5'
    open_weather_dict = dict()
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as result:
            body = await result.text()
    res = json.loads(body)
    open_weather_dict['now'] = res['list'][0]
    open_weather_dict['now']['main']['temp_avg'] = (open_weather_dict['now']['main']['temp_min'] +
                                                    open_weather_dict['now']['main']['temp_max']) / 2
    for i in range(1, 4):
        next_time = f'after {i * 3} h'
        res['list'][i]['main']['temp_avg'] = (res['list'][i]['main']['temp_min'] + res['list'][i]['main'][
            'temp_max']) / 2
        open_weather_dict[next_time] = res['list'][i]
    for i in open_weather_dict:
        open_weather_dict[i] = {'temp': open_weather_dict[i]['main']['temp_avg'],
                                'sky': open_weather_dict[i]['weather'][0]['description'].lower()}
    print('open_weathrer is done')
    return open_weather_dict


async def api_weather(lat, lon, weather_token, sky):
    url_now = f'http://api.weatherapi.com/v1/current.json?key={weather_token}&q={lat},{lon}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url_now) as result_req:
            body = await result_req.text()
    res = json.loads(body)
    open_forecast_dict = {'now': res['current']}
    start_time = int(res['location']['localtime'].split()[1].split(':')[0]) + 1
    url_fore = f'http://api.weatherapi.com/v1/forecast.json?key={weather_token}&q={lat},{lon}&days=2'
    result_req = req.get(url_fore)
    res = json.loads(result_req.text)
    x = 0
    last_hour = start_time - 1
    for i in range(start_time + 2, 24, 3):
        if len(open_forecast_dict) < 5:
            x += 3
            open_forecast_dict[f'after {x} h'] = res['forecast']['forecastday'][0]['hour'][i]
            last_hour = int(open_forecast_dict[f'after {x} h']['time'].split()[1].split(':')[0])
    if len(open_forecast_dict) < 4:
        start_hour_next_day = last_hour - 21
        for i in range(1, 5 - len(open_forecast_dict)):
            x += 3
            open_forecast_dict[f'after {x} h'] = res['forecast']['forecastday'][0]['hour'][start_hour_next_day]
            start_hour_next_day += 3
    for i in open_forecast_dict:
        open_forecast_dict[i] = {'temp': open_forecast_dict[i]['temp_c'],
                                 'sky': sky[str(open_forecast_dict[i]['condition']['code'])]['ru'].lower()}
    print('api_weather is done')
    return open_forecast_dict


# def yandex_weather(latitude, longitude, token_yandex: str):
#    url_yandex = f'https://api.weather.yandex.ru/v2/informers/?lat={latitude}&lon={longitude}&[lang=ru_RU]'
#    yandex_req = req.get(url_yandex, headers={'X-Yandex-API-Key': token_yandex}, verify=False)
#    conditions = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
#                  'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
#                  'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
#                  'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
#                  'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
#                  'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
#                  'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
#                  }
#    wind_dir = {'nw': 'северо-западное', 'n': 'северное', 'ne': 'северо-восточное', 'e': 'восточное',
#                'se': 'юго-восточное', 's': 'южное', 'sw': 'юго-западное', 'w': 'западное', 'с': 'штиль'}
#
#    yandex_json = json.loads(yandex_req.text)
#    yandex_json['fact']['condition'] = conditions[yandex_json['fact']['condition']]
#    yandex_json['fact']['wind_dir'] = wind_dir[yandex_json['fact']['wind_dir']]
#    for parts in yandex_json['forecast']['parts']:
#        parts['condition'] = conditions[parts['condition']]
#        parts['wind_dir'] = wind_dir[parts['wind_dir']]
#
#    pogoda = dict()
#    params = ['condition', 'wind_dir', 'pressure_mm', 'humidity']
#    for parts in yandex_json['forecast']['parts']:
#        pogoda[parts['part_name']] = dict()
#        pogoda[parts['part_name']]['temp'] = parts['temp_avg']
#        for param in params:
#            pogoda[parts['part_name']][param] = parts[param]
#
#    pogoda['fact'] = dict()
#    pogoda['fact']['temp'] = yandex_json['fact']['temp']
#    for param in params:
#        pogoda['fact'][param] = yandex_json['fact'][param]
#
#    pogoda['link'] = yandex_json['info']['url']
#    return pogoda


async def job_with_history(city_code, year, month_now, day):
    new_url = f'https://www.gismeteo.ru/diary/{city_code}/{year}/{month_now}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (HTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34'}
    async with aiohttp.ClientSession() as session:
        async with session.get(new_url, headers=headers) as result_req:
            body = await result_req.text()
    text = body
    search_text = r'<td class=first>' + str(day)
    search = text.find(search_text)
    day_history = text[search: search + 1100]
    search_temp = r"<td class='first_in_group"
    row_temp = day_history[day_history.find(search_temp) + 20: day_history.find(search_temp) + 40]
    row_temp = row_temp[row_temp.rfind("'>") + 2:]
    end_point = r'<'
    try:
        temp = float(row_temp[:row_temp.find(end_point)])
    except Exception as err:
        print(err)
        temp = 0
    sky_poss = {'suncl-bw': 'облачно', 'dull-bw': 'пасмурно', 'sunc-bw': 'малооблачно', 'sun-bw': 'ясно'}
    for sky in sky_poss.keys():
        number_start = day_history.find(sky)
        if number_start > 0:
            row_sky = day_history[number_start:number_start + 10]
            row_sky = row_sky[:row_sky.find('.')]
            sky_p = sky_poss[row_sky]
            break
        else:
            sky_p = 'ясно'
    return temp, sky_p


async def history_weather(city):
    x_url = Google.search('gismeteo' + city + ' 3 дня')[0].link
    x_simbol = x_url[0:-8].rfind('-')
    city_code = x_url[x_simbol + 1:-8]
    now = datetime.now()
    month_now = datetime.date(now).month
    year_now = datetime.date(now).year
    day = datetime.date(now).day
    list_temp = []
    list_sky = []
    tasks = []
    for year in range(year_now - 1, year_now - 11, -1):
        tasks.append(asyncio.create_task(job_with_history(city_code, year, month_now, day)))
    responses = await asyncio.gather(*tasks)
    for i in responses:
        list_temp.append(i[0])
        list_sky.append(i[1])
    dict_sky = {'ясно': 0, 'малооблачно': 0, 'облачно': 0, 'пасмурно': 0}
    for i in list_sky:
        dict_sky[i] += 1
    median_sky = max(dict_sky)
    list_temp = sorted(list_temp)
    avg_temp = round(sum(list_temp) / len(list_temp), 2)
    min_temp = min(list_temp)
    max_temp = max(list_temp)
    print('history is done')
    return avg_temp, min_temp, max_temp, median_sky, day, month_now, year_now


token = environ['token_bot']
token_accu = environ['token_accu']
token_yandex = environ['token_yandex']
open_token = environ['open_token']
