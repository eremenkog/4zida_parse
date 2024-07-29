import os
import telebot
from dotenv import load_dotenv
import pandas as pd
from telebot.types import InputMediaPhoto


load_dotenv('token.env')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


def get_random_apartment(file_path='output.csv'):
    df = pd.read_csv(file_path)
    
    # Выбираем случайную строку, кроме первой (с заголовками)
    random_row = df.sample(n=1).iloc[0]

    apartment_info = {
        'Address': random_row['Address'],
        'Price': random_row['Price'],
        'Price per square': random_row['Price per square'],
        'Area': random_row['Area'],
        'Preview': random_row['Preview'],
        'Link': random_row['Link']
    }
    return apartment_info

@bot.message_handler(commands=['random'])
def send_random_asmediagroup(*args):
    apartment = get_random_apartment()
    caption = (
        f"<b>{apartment['Address']}</b>\n"
        f"Price: {apartment['Price']}€\n"
        f"Price per square: {apartment['Price per square']}€/m²\n"
        f"Area: {apartment['Area']}m²\n"
        f"Link: {apartment['Link']}"
    )

    bot.send_media_group(
        chat_id=CHAT_ID,
        media= [InputMediaPhoto('{0}'.format(apartment['Preview']), caption=caption)],
        disable_notification=True
        )

bot.infinity_polling()