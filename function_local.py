# import sys
# sys.path.insert(0, '/usr/lib/python3.10/site-packages')

# import telebot
from function_import import *
from os import environ
import asyncio
# from tokensy import environ


token = environ['token_bot']
weather_token = environ['weather_token']
open_token = environ['open_token']
token_accu = environ['token_accu']

with open('sky.json', encoding='utf-8') as f:
    sky = json.load(f)


async def print_weather(dict_weather, message):
    await message.answer(f'Разрешите доложить, Ваше сиятельство!'
                         f' Температура сейчас {dict_weather["now"]["temp"]}!\n'
                         f' А на небе {dict_weather["now"]["sky"]}.\n'
                         f' Температура через три часа {dict_weather["after 3 h"]["temp"]}!\n'
                         f' А на небе {dict_weather["after 3 h"]["sky"]}.\n'
                         f' Температура через шесть часов {dict_weather["after 6 h"]["temp"]}!\n'
                         f' А на небе {dict_weather["after 6 h"]["sky"]}.\n'
                         f' Температура через девять часов {dict_weather["after 9 h"]["temp"]}!\n'
                         f' А на небе {dict_weather["after 9 h"]["sky"]}.')


async def add_city(message, cities):
    try:
        city = message.text.lower().split('город ')[1]
        lat, lon = geo_pos(city)
        code = await code_location(lat, lon, token_accu)
        cities[str(message.from_user.id)] = {'city': city, 'lat': lat, 'lon': lon, 'cod_loc': code}
        with open('cities.json', 'w') as f:
            json.dump(cities, f)
        with open('cities.json', encoding='utf-8') as x:
            cities_test = json.load(x)
        return cities_test, 0
    except Exception as err:
        print(err)
        return cities, 1


async def big_weather(message, sky, cities, city):
    tasks = []
    if city is None:
        cod_loc = cities[str(message.from_user.id)]['cod_loc']
        lat = cities[str(message.from_user.id)]['lat']
        lon = cities[str(message.from_user.id)]['lon']
    else:
        lat, lon = geo_pos(city)
        cod_loc = await code_location(lat, lon, token_accu)

    total_weather_dict = dict()
    try:
        tasks.append(asyncio.create_task(weather(cod_loc, token_accu)))
        tasks.append(asyncio.create_task(open_weather(lat, lon, open_token)))
        tasks.append(asyncio.create_task(api_weather(lat, lon, weather_token, sky)))
        responses = await asyncio.gather(*tasks)
        total_weather_dict['accu_weather'] = responses[0]
        total_weather_dict['open_weather'] = responses[1]
        total_weather_dict['api_weather'] = responses[2]

    except Exception as err:
        print(err)
        tasks.append(asyncio.create_task(open_weather(lat, lon, open_token)))
        tasks.append(asyncio.create_task(api_weather(lat, lon, weather_token, sky)))
        responses = await asyncio.gather(*tasks)
        total_weather_dict['open_weather'] = responses[0]
        total_weather_dict['api_weather'] = responses[1]

        total_weather_dict['accu_weather'] = total_weather_dict['open_weather']

    times = ['now', 'after 3 h', 'after 6 h', 'after 9 h']
    main_weather = dict()
    for i in times:
        main_weather[i] = dict()
        list_temp = sorted(
            [total_weather_dict['accu_weather'][i]['temp'], total_weather_dict['open_weather'][i]['temp'],
             total_weather_dict['api_weather'][i]['temp']])
        main_weather[i]['temp'] = round(list_temp[1], 2)
        if total_weather_dict['accu_weather'][i]['sky'] in (total_weather_dict['open_weather'][i]['sky'],
                                                            total_weather_dict['api_weather'][i]['sky']):
            main_weather[i]['sky'] = total_weather_dict['accu_weather'][i]['sky']
        elif total_weather_dict['api_weather'][i]['sky'] == total_weather_dict['open_weather'][i]['sky']:
            main_weather[i]['sky'] = total_weather_dict['api_weather'][i]['sky']
        else:
            list_sky = [total_weather_dict["accu_weather"][i]["sky"].lower(),
                        total_weather_dict["open_weather"][i]["sky"],
                        total_weather_dict["api_weather"][i]["sky"]]
            main_weather[i]['sky'] = f'{total_weather_dict["accu_weather"][i]["sky"]} или' \
                                     f' {total_weather_dict["open_weather"][i]["sky"]} или' \
                                     f' {total_weather_dict["api_weather"][i]["sky"]}'
            chek_sky = main_weather[i]['sky']
            chek_sky = chek_sky.replace('или ', '')

            max_count = 0
            print(list_sky)

    await print_weather(main_weather, message)
