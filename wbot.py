from os import environ, path

# import asyncio
import logging
import sys
#from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
import json
import tokensy
from function_local import *

# TOKEN = str(getenv(environ['token_bot']))  # tokensy.environ['token_bot']
TOKEN = environ['token_bot']
token_accu = environ['token_accu']
token_yandex = environ['token_yandex']

dp = Dispatcher()

with open('cities.json', encoding='utf-8') as f:
    cities = json.load(f)
with open('sky.json', encoding='utf-8') as f:
    sky = json.load(f)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """

    await message.answer(f"Я погодабот, приятно познакомиться, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: Message) -> None:
    global cities
    user_id = str(message.from_user.id)

    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    match message.text.lower().split(" "):
        case ['привет'] | ['здарова']:
            await message.answer(f'О великий и могучий {message.from_user.full_name}! '
                                 f'Позвольте Я доложу Вам о погоде! Напишите  слово'
                                 f' "погода" и я напишу погоду в Вашем "стандартном" городе'
                                 f' или напишите название города в котором Вы сейчас')
        case ['погода']:
            if user_id in cities.keys():
                city = cities[user_id]['city']
                await message.answer(f'О великий и могучий {message.from_user.first_name}!'
                                     f' Твой город {city}')
                await big_weather(message, sky, cities, None)

                print('big_weather is done')
                avg_temp, min_temp, max_temp, avg_sky, day, month, year_now = await history_weather(city)
                await message.answer(f'Историческая справка на {day}.{month}.{year_now} для города'
                                     f' {city}:\n Средняя температура в этот день: {avg_temp}\n'
                                     f'Максимальная температура за 10 лет в этот день {max_temp}\n'
                                     f'Минимальная температура за 10 лет в этот день {min_temp}\n'
                                     f'Среднее небо {avg_sky}.')

            else:
                await message.answer(f'О великий и могучий {message.from_user.first_name}!'
                                     f' Я не знаю Ваш город! Просто напиши:'
                                     f'"Мой город *****" и я запомню твой стандартный город!')

        case ['мой', 'город', _]:
            print(message.text[10:])
            cities, flag = await add_city(message, cities)
            if flag == 0:
                await message.answer(f'О великий и могучий {message.from_user.first_name}!'
                                     f' Теперь я знаю Ваш город! это'
                                     f' {cities[str(message.from_user.id)]["city"]}')
            else:
                await message.answer(f'О великий и могучий {message.from_user.first_name}!'
                                     f' Что то пошло не так :(')
        case _:
            try:
                city = message.text.strip()
                await message.answer(f'Привет {message.from_user.first_name}! Твой город {city}')
                await big_weather(message, sky, cities, city)

            except AttributeError as err:
                await message.answer(f'{message.from_user.first_name}! Не вели казнить,'
                                     f' вели слово молвить! Я не нашел такого города!'
                                     f'И получил ошибку {err}, попробуй другой город')


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
