import telebot;
from telebot import types
import os
from dotenv import load_dotenv

name = ''
surname = ''
age = 0

# loading variables from .env file
load_dotenv()

# Getting token
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, "What is your name?")
        bot.register_next_step_handler(message, get_name) #next step – function get_name
    else:
        bot.send_message(message.from_user.id, 'Write /reg')

def get_name(message): # Get the surname
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'What is your surname?')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'how old are you?')
    bot.register_next_step_handler(message, get_age)

def get_age(message):
    global age
    while age == 0: # Check that age has changed
        try:
             age = int(message.text) # Check that age was entered correctly
        except Exception:
             bot.send_message(message.from_user.id, 'In figures, please')
    keyboard = types.InlineKeyboardMarkup() # Our keyboard
    key_yes = types.InlineKeyboardButton(text='Yes', callback_data='yes'); # "Yes" button
    keyboard.add(key_yes); # Add button to the keyboard
    key_no= types.InlineKeyboardButton(text='No', callback_data='no')
    keyboard.add(key_no)
    question = 'Are '+str(age)+' years old, and your name: '+name+' '+surname+'?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": # call.data is the callback_data specified when declaring the button
        # Code for saving data, or processing it
        bot.send_message(call.message.chat.id, 'nice')
    else:
        # Ask again
        bot.send_message(call.message.chat.id, 'bad')
        bot.register_next_step_handler(message, start) # Next step - start function

bot.polling(none_stop=True, interval=0)