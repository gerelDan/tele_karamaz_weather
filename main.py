import json
import telebot

import requests as req
from tokensy import tokenoga, token_accu, token_yandex

from geopy import geocoders


token = tokenoga

def code_location(location: str, token_accu: str):
    url_location = f'http://dataservice.accuweather.com/locations/v1/cities/autocomplete?apikey=' \
                   f'{token_accu}&q={location}&language=ru'
    response = req.get(url_location, headers={"APIKey" : token_accu})
    json_data = json.loads(response.text)
    code = json_data[0]['Key']
    return code

def weather(cod_loc: str, token_accu: str):
    url_weather = f'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{cod_loc}?apikey={token_accu}&language=ru&metric=True'
    response = req.get(url_weather, headers={"APIKey": token_accu})
    json_data = json.loads(response.text)
    dict_weather = dict()
    dict_weather['link'] = json_data[0]['MobileLink']
    for i in range(len(json_data)):
        time = 'сейчас'
        if i != 0:
            time = 'через' + str(i) + 'ч'
        dict_weather[time] = {'temp': json_data[i]['Temperature']['Value'], 'sky': json_data[i]['IconPhrase']}
        dict_weather['temp'] = json_data[i]['Temperature']['Value']
    return dict_weather

def  print_weather(dict_weather, message):
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
    bot.send_message(message.from_user.id, f'А яндекс говорит:'
                                           f' Температура сейчас {dict_weather_yandex["fact"]["temp"]}!'
                                           f' А на небе {dict_weather_yandex["fact"]["condition"]}.'
                                           f' Сегодня ночью температура {dict_weather_yandex["night"]["temp"]}.'
                                           f' А на небе {dict_weather_yandex["night"]["condition"]}.'
                                           f' Температура утром {dict_weather_yandex["morning"]["temp"]}.'
                                           f' А на небе {dict_weather_yandex["morning"]["condition"]}.'
                                           f' Температура днем {dict_weather_yandex["day"]["temp"]}.'
                                           f' А на небе {dict_weather_yandex["day"]["condition"]}.'
                                           f' Температура вечером {dict_weather_yandex["evening"]["temp"]}.'
                                           f' А на небе {dict_weather_yandex["evening"]["condition"]}.')
    bot.send_message(message.from_user.id, f' А здесь ссылка на подробности '
                                           f'{dict_weather_yandex["link"]}')


def geo_pos(city: str):
    geolocator = geocoders.Nominatim(user_agent="telebot")
    latitude = str(geolocator.geocode(city).latitude)
    longitude = str(geolocator.geocode(city).longitude)
    return latitude, longitude


def yandex_weather(latitude, longitude, token_yandex: str):
    url_yandex = f'https://api.weather.yandex.ru/v2/forecast/?lat={latitude}&lon={longitude}&[lang=ru_RU]'
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
    sutki = ['night', 'morning', 'day', 'evening']
    pogoda = dict()
    for vremya in sutki:
        pogoda[vremya] = dict()
        pogoda[vremya]['temp'] = yandex_json['forecasts'][0]['parts'][vremya]['temp_avg']
        pogoda[vremya]['condition'] = conditions[yandex_json['forecasts'][0]['parts'][vremya]['condition']]
        pogoda[vremya]['wind_dir'] = wind_dir[yandex_json['forecasts'][0]['parts'][vremya]['wind_dir']]
        pogoda[vremya]['pressure_mm'] = yandex_json['forecasts'][0]['parts'][vremya]['pressure_mm']
        pogoda[vremya]['humidity'] = yandex_json['forecasts'][0]['parts'][vremya]['humidity']

    pogoda['fact'] = dict()
    pogoda['fact']['temp'] = yandex_json['fact']['temp']
    pogoda['fact']['condition'] = conditions[yandex_json['fact']['condition']]
    pogoda['fact']['wind_dir'] = wind_dir[yandex_json['fact']['wind_dir']]
    pogoda['fact']['pressure_mm'] = yandex_json['fact']['pressure_mm']
    pogoda['fact']['humidity'] = yandex_json['fact']['humidity']
    pogoda['link'] = yandex_json['info']['url']
    return pogoda


bot = telebot.TeleBot(token)

cities = dict(zip(['Pavel', 'Kirill', 'Aleksey', 'Daniil'], ['Новосибирск', 'Усть-Илимск', 'Красноярск', 'Нягань']))

@bot.message_handler(command = ['start', 'help'])
def send_welcome(message):
  bot.reply_to(message, f'Я погодабот, приятно познакомитсья, {message.from_user.first_name}')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет' or message.text.lower() ==  'здорова':
        bot.send_message(message.from_user.id, f'О великий и могучий {message.from_user.first_name}! Позвольте Я доложу '
                                               f' Вам о погоде! Напишите  слово "погода" и я напишу погоду в Вашем'
                                               f' "стандартном" городе или напишите название города в готором Вы сейчас')
    elif message.text.lower() == 'погода' and message.from_user.first_name in cities.keys():
        city = cities[message.from_user.first_name]
        bot.send_message(message.from_user.id, f'О великий и могучий {message.from_user.first_name}! Твой город {city}')
        cod_loc = code_location(city, token_accu)
        you_weather = weather(cod_loc, token_accu)
        print_weather(you_weather, message)
        latitude = geo_pos(city)[0]
        print(latitude)
        longitude = geo_pos(city)[1]
        print(longitude)
        yandex_weather_x = yandex_weather(latitude, longitude, token_yandex)
        print(yandex_weather_x)
        print_yandex_weather(yandex_weather_x, message)


    elif message.text.lower() == 'погода':
        bot.send_message(message.from_user.id, f'О великий и могучий {message.from_user.first_name}!'
                                               f' Я не знаю Ваш город! Просто напиши свой город!')
    else:
        try:
            city = message.text
            bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}! Твой город {city}')
            cod_loc = code_location(city, token_accu)
            you_weather = weather(cod_loc, token_accu)
            print_weather(you_weather, message)
            latitude, longitude = geo_pos(city)
            yandex_weather_x = yandex_weather(latitude, longitude, token_yandex)
            print_yandex_weather(yandex_weather_x, message)
        except Exception as err:
            bot.send_message(message.from_user.id, f'{message.from_user.first_name}! Не вели казнить,'
                                                   f' вели слово молвить! Я не нашел такого города!'
                                                   f'И получил ошибку {err}, попробуй другой город')

bot.polling(none_stop=True)
