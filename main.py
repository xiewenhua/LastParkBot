import telebot
import os
import time
import datetime
import pytz
import threading
import sys
import json

all_variables = os.environ
bot = telebot.TeleBot(all_variables.get('BOT_TOKEN'))
my_chat_id = all_variables.get('MY_CHAT_ID')
github_run_id = str(all_variables.get('GITHUB_RUN_ID'))
runtime = 3
if "GITHUB_ACTIONS" in all_variables:
    runtime = int(all_variables.get('RUNTIME')) * 3600


def get_beijing_time():
    timezone = pytz.timezone('Asia/Shanghai')
    now = datetime.datetime.now()
    return now


@bot.message_handler(commands=['stop'])
def exit_program():
    end_message = log_message('本次服务已结束')
    bot.send_message(my_chat_id, end_message)
    print(end_message)
    bot.stop_polling()


def log_message(message):
    beijing_time = get_beijing_time()
    message = github_run_id + ' ' + \
        beijing_time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + message
    return message


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "你好，请问需要什么服务")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


def start_program():
    start_message = log_message('服务已启动')
    bot.send_message(my_chat_id, start_message)
    print(start_message)


start_program()

# 因为是github action执行，所以定时停止
timer = threading.Timer(runtime, exit_program)
timer.start()
bot.polling()

print('本次服务已结束')
sys.exit(0)
