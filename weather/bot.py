import telebot
import requests
import os
from dotenv import load_dotenv
from main import Log, session

load_dotenv()
token = os.getenv('token')

bot = telebot.TeleBot(token)

dictionary = {
    'Overcast': 'пасмурно',
    'Partly Cloudy': 'переменная облачность',
    'Blowing snow': 'идет снег',
    'Sunny': 'cолнечно'
}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Бот был создан для в качестве теста для компании BobrAi. Введите команду /weather <город> для получения информации о погоде в указанном городе")


@bot.message_handler(content_types=["text"])
def echo(message):
    if "/weather" in message.text:
        text = message.text
        if len(text) > 8:
            city = text.split(' ')[1]
            data = requests.get(f"http://api.weatherapi.com/v1/current.json?key=bf5252575ee04f82b0c141528241010&q={city}&aqi=no").json()
            if data.get('error'):
                bot.send_message(message.chat.id, "Город указан неверно")
            else:
                description = dictionary.get(data['current']['condition']['text'], data['current']['condition']['text'])
                answer = f"В {city} сейчас: {description}, температура {data['current']['temp_c']} градусов цельсия, ощущаемая температура {data['current']['feelslike_c']} градусов цельсия, влажность {data['current']['humidity']}, cкорость ветра {data['current']['wind_kph']} км/ч"
                new_item = Log(user_id=message.from_user.id, command=text, answer=answer)
                session.add(new_item)
                session.commit()
                bot.send_message(message.chat.id, answer)
        else:
            bot.send_message(message.chat.id, "Город не указан")


bot.polling(none_stop=True)
