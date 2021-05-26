import json
import telebot

bot = telebot.TeleBot('1475943543:AAHFfTlaUt4NLmLjqY74MwxCLkVJkT9DrRQ')

@bot.message_handler(command = ['start', 'help'])
def send_welcome(message):
  bot.reply_to(message, f'Я погодабот, приятно познакомитсья, {message.from_user.first_name}')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.from_user.id, 'Привет!')
    else:
        bot.send_message(message.from_user.id, 'Не понимаю, что это значит.')
#print('Hello World')

bot.polling(none_stop=True)
© 2021 GitHub, Inc.