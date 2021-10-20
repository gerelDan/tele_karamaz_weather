import json
import telebot
import requests as req
from geopy import geocoders
from os import environ

token = environ['token_bot']
token_accu = environ['token_accu']
token_yandex = environ['token_yandex']


def code_location(latitude: str, longitude: str, token_accu: str):
    url_location_key = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=' \
                       f'{token_accu}&q={latitude},{longitude}&language=ru'
    resp_loc = req.get(url_location_key, headers={"APIKey": token_accu})
    json_data = json.loads(resp_loc.text)
    code = json_data['Key']
    return code


def weather(code_loc: str, token_accu: str):
    url_weather = f'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{code_loc}?' \
                  f'apikey={token_accu}&language=ru&metric=True'
    response = req.get(url_weather, headers={"APIKey": token_accu})
    json_data = json.loads(response.text)
    dict_weather = dict()
    dict_weather['link'] = json_data[0]['MobileLink']
    time = 'сейчас'
    dict_weather[time] = {'temp': json_data[0]['Temperature']['Value'], 'sky': json_data[0]['IconPhrase']}
    for i in range(1, len(json_data)):
        time = 'через' + str(i) + 'ч'
        dict_weather[time] = {'temp': json_data[i]['Temperature']['Value'], 'sky': json_data[i]['IconPhrase']}
    return dict_weather


def print_weather(dict_weather, message):
    bot.send_message(message.from_user.id, f'Разрешите доложить, Ваше сиятельство!'
                                           f' Температура сейчас {dict_weather["сейчас"]["temp"]}!'
                                           f' А на небе {dict_weather["сейчас"]["sky"]}.'
                                           f' Температура через три часа {dict_weather["через3ч"]["temp"]}!'
                                           f' А на небе {dict_weather["через3ч"]["sky"]}.'
                                           f' Температура через шесть часов {dict_weather["через6ч"]["temp"]}!'
                                           f' А на небе {dict_weather["через6ч"]["sky"]}.'
                                           f' Температура через девять часов {dict_weather["через9ч"]["temp"]}!'
                                           f' А на небе {dict_weather["через9ч"]["sky"]}.')
    bot.send_message(message.from_user.id, f' А здесь ссылка на подробности '
                                           f'{dict_weather["link"]}')


def print_yandex_weather(dict_weather_yandex, message):
    day = {'night': 'ночью', 'morning': 'утром', 'day': 'днем', 'evening': 'вечером', 'fact': 'сейчас'}
    bot.send_message(message.from_user.id, f'А яндекс говорит:')
    for i in dict_weather_yandex.keys():
        if i != 'link':
            time_day = day[i]
            bot.send_message(message.from_user.id, f'Температура {time_day} {dict_weather_yandex[i]["temp"]}'
                                                   f', на небе {dict_weather_yandex[i]["condition"]}')

    bot.send_message(message.from_user.id, f' А здесь ссылка на подробности '
                                           f'{dict_weather_yandex["link"]}')


def geo_pos(city: str):
    geolocator = geocoders.Nominatim(user_agent="telebot")
    latitude = str(geolocator.geocode(city).latitude)
    longitude = str(geolocator.geocode(city).longitude)
    return latitude, longitude


def yandex_weather(latitude, longitude, token_yandex: str):
    url_yandex = f'https://api.weather.yandex.ru/v2/informers/?lat={latitude}&lon={longitude}&[lang=ru_RU]'
    yandex_req = req.get(url_yandex, headers={'X-Yandex-API-Key': token_yandex}, verify=False)
    conditions = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
                  'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
                  'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
                  'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
                  'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
                  'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
                  'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
                  }
    wind_dir = {'nw': 'северо-западное', 'n': 'северное', 'ne': 'северо-восточное', 'e': 'восточное',
                'se': 'юго-восточное', 's': 'южное', 'sw': 'юго-западное', 'w': 'западное', 'с': 'штиль'}

    yandex_json = json.loads(yandex_req.text)
    yandex_json['fact']['condition'] = conditions[yandex_json['fact']['condition']]
    yandex_json['fact']['wind_dir'] = wind_dir[yandex_json['fact']['wind_dir']]
    for parts in yandex_json['forecast']['parts']:
        parts['condition'] = conditions[parts['condition']]
        parts['wind_dir'] = wind_dir[parts['wind_dir']]

    weather = dict()
    params = ['condition', 'wind_dir', 'pressure_mm', 'humidity']
    for parts in yandex_json['forecast']['parts']:
        weather[parts['part_name']] = dict()
        weather[parts['part_name']]['temp'] = parts['temp_avg']
        for param in params:
            weather[parts['part_name']][param] = parts[param]

    weather['fact'] = dict()
    weather['fact']['temp'] = yandex_json['fact']['temp']
    for param in params:
        weather['fact'][param] = yandex_json['fact'][param]

    weather['link'] = yandex_json['info']['url']
    return weather


def add_city(message):
    try:
        latitude, longitude = geo_pos(message.text.lower().split('город ')[1])
        global cities
        cities[message.from_user.id] = message.text.lower().split('город ')[1]
        with open('cities.json', 'w') as f:
            f.write(json.dumps(cities))
        return cities, 0
    except Exception as err:
        return cities, 1


bot = telebot.TeleBot(token)

with open('cities.json', encoding='utf-8') as f:
    cities = json.load(f)


@bot.message_handler(command=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f'Я погодабот, приятно познакомитсья, {message.from_user.first_name}')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global cities
    if message.text.lower() == 'привет' or message.text.lower() == 'здорова':
        bot.send_message(message.from_user.id,
                         f'О великий и могучий {message.from_user.first_name}! Позвольте Я доложу '
                         f' Вам о погоде! Напишите  слово "погода" и я напишу погоду в Вашем'
                         f' "стандартном" городе или напишите название города в готором Вы сейчас')
    elif message.text.lower() == 'погода':
        if message.from_user.id in cities.keys():
            city = cities[message.from_user.id]
            bot.send_message(message.from_user.id, f'О великий и могучий {message.from_user.first_name}!'
                                                   f' Твой город {city}')
            latitude, longitude = geo_pos(city)
            code_loc = code_location(latitude, longitude, token_accu)
            you_weather = weather(code_loc, token_accu)
            print_weather(you_weather, message)
            yandex_weather_x = yandex_weather(latitude, longitude, token_yandex)
            print_yandex_weather(yandex_weather_x, message)
        else:
            bot.send_message(message.from_user.id, f'О великий и могучий {message.from_user.first_name}!'
                                                   f' Я не знаю Ваш город! Просто напиши:'
                                                   f'"Мой город *****" и я запомню твой стандартный город!')
    elif message.text.lower()[:9] == 'мой город':
        cities, flag = add_city(message)
        if flag == 0:
            bot.send_message(message.from_user.id, f'О великий и могучий {message.from_user.first_name}!'
                                                   f' Теперь я знаю Ваш город! это'
                                                   f' {cities[message.from_user.id]}')
        else:
            bot.send_message(message.from_user.id, f'О великий и могучий {message.from_user.first_name}!'
                                                   f' Что то пошло не так :(')
    else:
        try:
            city = message.text
            bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}! Твой город {city}')
            latitude, longitude = geo_pos(city)
            code_loc = code_location(latitude, longitude, token_accu)
            you_weather = weather(code_loc, token_accu)
            print_weather(you_weather, message)
            yandex_weather_x = yandex_weather(latitude, longitude, token_yandex)
            print_yandex_weather(yandex_weather_x, message)
        except AttributeError as err:
            bot.send_message(message.from_user.id, f'{message.from_user.first_name}! Не вели казнить,'
                                                   f' вели слово молвить! Я не нашел такого города!'
                                                   f'И получил ошибку {err}, попробуй другой город')


bot.polling(none_stop=True)

