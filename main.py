import json
import telebot
import requests as req
from tokensy import tokenoga, token_accu

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

bot = telebot.TeleBot(token)

cities = dict(zip(['Pavel', 'Kirill', 'Aleksey', 'Daniil'], ['Новосибирск', 'Усть-Илимск', 'Красноярск', 'Нягань']))

@bot.message_handler(command = ['start', 'help'])
def send_welcome(message):
  bot.reply_to(message, f'Я погодабот, приятно познакомитсья, {message.from_user.first_name}')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет' or message.text.lower() ==  'здорова':
        bot.send_message(message.from_user.id, f'О великий и могучи {message.from_user.first_name}! Позволь Я доложу '
                                               f' Вам о погоде! Напишите  слово "погода" и я напишу погоду в Вашем'
                                               f' "стандартном" городе или напишите название города в готором Вы сейчас')
    elif message.text.lower() == 'погода':
        city = cities[message.from_user.first_name]
        bot.send_message(message.from_user.id, f'О великий и могучий {message.from_user.first_name}! Твой город {city}')
        cod_loc = code_location(city, token_accu)
        you_weather = weather(cod_loc, token_accu)
        print_weather(you_weather, message)

    else:
        try:
            city = message.text
            bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}! Твой город {city}')
            cod_loc = code_location(city, token_accu)
            you_weather = weather(cod_loc, token_accu)
            print_weather(you_weather, message)
        except Exception as err:
            bot.send_message(message.from_user.id, f'{message.from_user.first_name}! Я не нашел такого города!'
                                                   f'И получил ошибку {err}, попробуй другой город')

bot.polling(none_stop=True)
#© 2021 GitHub, Inc.