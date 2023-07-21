import os
import telebot
import datetime
import requests
import key
from prettytable import PrettyTable

bot = telebot.TeleBot(key.BOT_KEY)
WEATHER = key.WEATHER_KEY

school_schedule = {
  'Monday': {
    'K102': {
      'class_name': 'PBO',
      'start_time': '07:00'
    },
    'E102': {
      'class_name': 'ALIN',
      'start_time': '13:00'
    },
    'LAB B': {
      'class_name': 'PRK.JRKM',
      'start_time': '18:15'
    }
  },
  'Tuesday': {
    'K102': {
      'class_name': 'JARKOM',
      'start_time': '07:00'
    },
    '': {
      'class_name': 'RPL',
      'start_time': '09:40'
    }
  },
  'Wednesday': {
    'K102': {
      'class_name': 'SISCER',
      'start_time': '07:00'
    },
    'E101': {
      'class_name': 'ASA',
      'start_time': '09:40'
    },
    'LAB A': {
      'class_name': 'PRK.PBO',
      'start_time': '13:00'
    }
  },
  'Thursday': {
    'Lab A': {
      'class_name': 'PRK.ASA',
      'start_time': '15:40'
    }
  },
  'Friday': {
    'K102': {
      'class_name': 'MBD',
      'start_time': '07:00'
    }
  }
}

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/hello - Greet the bot\n"
        "/weather - Get the current weather\n"
        "/addtodo <task> - Add a task to the to-do list\n"
        "/listtodos - List all to-do items\n"
        "/removetodo <index> - Remove a to-do item by index\n"
        "/schedule - Get today's school schedule\n"
        "/help - Show this help message\n"
        "/terminate - Terminate the program (for the bot owner only)"
    )
    bot.send_message(chat_id=message.chat.id, text=help_text)

@bot.message_handler(commands=['start'])
def start(message):
  bot.send_message(message.chat.id, "READY!!!")


@bot.message_handler(commands=['hello'])
def greet(message):
  bot.send_message(message.chat.id, "Hey!")


@bot.message_handler(commands=['weather'])
def get_weather(message):
  # Replace YOUR_API_KEY with your actual API key from OpenWeatherMap
  city = "Semarang"
  url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER}"
  response = requests.get(url).json()
  if response['cod'] != '404':
    # Get the temperature in Celsius
    temperature = round(response['main']['temp'] - 273.15, 2)
    # Get the weather description (e.g. cloudy, sunny, etc.)
    description = response['weather'][0]['description']
    # Format the message and send it to the user
    message_text = f"The current weather in {city} is {description} with a temperature of {temperature}°C."
    bot.send_message(chat_id=message.chat.id, text=message_text)
  else:
    bot.send_message(
      chat_id=message.chat.id,
      text=
      "Sorry, I couldn't retrieve weather data at this time. Please try again later"
    )


todos = {}


@bot.message_handler(commands=['addtodo'])
def add_todo_item(message):
  chat_id = message.chat.id
  text = message.text.split(maxsplit=1)[1]
  if chat_id not in todos:
    todos[chat_id] = []
  todos[chat_id].append(text)
  bot.reply_to(message, f'To-do item added: {text}')


@bot.message_handler(commands=['listtodos'])
def list_todo_items(message):
  chat_id = message.chat.id
  if chat_id not in todos:
    bot.reply_to(message, 'No to-do items yet!')
  else:
    items = '\n'.join(todos[chat_id])
    bot.reply_to(message, f'To-do list:\n{items}')


@bot.message_handler(commands=['removetodo'])
def remove_todo_item(message):
  chat_id = message.chat.id
  index = int(message.text.split(maxsplit=1)[1])
  if chat_id not in todos or index >= len(todos[chat_id]):
    bot.reply_to(message, 'Invalid index!')
  else:
    item = todos[chat_id].pop(index)
    bot.reply_to(message, f'To-do item removed: {item}')


@bot.message_handler(commands=['schedule'])
def send_schedule(message):
  day_of_week = datetime.datetime.today().strftime('%A')
  if day_of_week in school_schedule:
    schedule_list = school_schedule[day_of_week]
    table = PrettyTable(['Time', 'Room', 'Class Name'])
    for room, class_info in schedule_list.items():
      class_name = class_info['class_name']
      start_time = class_info['start_time']
      table.add_row([start_time, room, class_name])
    bot.send_message(
      chat_id=message.chat.id,
      text=
      f'Here is the schedule for {day_of_week}:\n```{table.get_string()}```',
      parse_mode='Markdown')
  else:
    bot.send_message(chat_id=message.chat.id, text='No school today!')

@bot.message_handler(commands=['terminate'])
def terminate_program(message):
    bot.reply_to(message, "Terminating the program...")
    bot.stop_polling()
    os._exit(0)

bot.polling()