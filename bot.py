import os, telebot, time, threading
from dotenv import load_dotenv
import pandas as pd
from telebot.types import InputMediaPhoto
from datetime import datetime

load_dotenv('token.env')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
stop_thread = threading.Event()

def get_random_apartment(file_path='output.csv'):
    df = pd.read_csv(file_path)
    
    filtered_df = df[df['Posted'].isnull()]
    if filtered_df.empty:
        return {}
    
    random_row = filtered_df.sample(n=1).iloc[0]

    apartment_info = {
        'Address': random_row['Address'],
        'Price': random_row['Price'],
        'Price per square': random_row['Price per square'],
        'Area': random_row['Area'],
        'Preview': random_row['Preview'],
        'Link': random_row['Link'] 
    }
    return apartment_info

def update_posted_timestamp(file_path, link):
    df = pd.read_csv(file_path)
    df.loc[df['Link'] == link, 'Posted'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv(file_path, index=False)

@bot.message_handler(commands=['random'])
def send_random_asmediagroup(*args):
    apartment = get_random_apartment()
    caption = (
        f"<b>{apartment['Address']}</b>\n"
        f"Price: {apartment['Price']}€\n"
        f"Price per square: {apartment['Price per square']}€/m²\n"
        f"Area: {apartment['Area']}m²\n"
        f"<a href='{apartment['Link']}'>Link</a>"
    )

    bot.send_media_group(
        chat_id=CHAT_ID,
        media= [InputMediaPhoto('{0}'.format(apartment['Preview']), caption=caption)],
        disable_notification=True
        )
    update_posted_timestamp('output.csv', apartment['Link'])

def auto_sender():
    while not stop_thread.is_set():
        send_random_asmediagroup()
        time.sleep(30)

@bot.message_handler(commands=['start'])
def start_sending(message):
    if not stop_thread.is_set():
        threading.Thread(target=auto_sender).start()
        bot.reply_to(message, "Started sending apartments every 30 seconds.")

@bot.message_handler(commands=['stop'])
def stop_sending(message):
    stop_thread.set()
    bot.reply_to(message, "Stopped sending apartments.")

bot.infinity_polling()