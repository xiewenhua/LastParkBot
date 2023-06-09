import telebot
import os
import time
from datetime import datetime, timedelta
import pytz
import threading
import sys
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import base64
import re

all_variables = os.environ
bot = telebot.TeleBot(all_variables.get('BOT_TOKEN'))
my_chat_id = all_variables.get('MY_CHAT_ID')
github_run_id = str(all_variables.get('GITHUB_RUN_ID'))
runtime = 600
if "GITHUB_ACTIONS" in all_variables:
    runtime = int(all_variables.get('RUNTIME'))

# 读取公钥
with open('public_key.pem', 'rb') as f:
    public_key = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )

# 读取私钥
with open('private_key.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

def encrypt_message(message):
    # 加密消息
    byte_string = message.encode('utf-8')
    encry_message = public_key.encrypt(
        byte_string,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encry_message = base64.b64encode(encry_message).decode('utf-8')
    return encry_message


def decrypt_message(message):
    # 解密消息
    byte_string = base64.b64decode(message)
    decrypted_message = private_key.decrypt(
        byte_string,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message.decode('utf-8')


@bot.message_handler(commands=['stop'])
def stop_server(message):
    reply_message = log_message('已成功停止本次服务')
    bot.reply_to(message, reply_message)
    bot.stop_polling()


def exit_program():
    end_message = log_message('本次服务已结束')
    bot.send_message(my_chat_id, end_message)
    print(end_message)
    bot.stop_polling()


def log_message(message):
    beijing_time = datetime.now()
    message = github_run_id + ' ' + \
        beijing_time.strftime("%Y-%m-%d %H:%M:%S") + ' ' + message
    return message


en_message = ''


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "你好，请问需要什么服务")


@bot.message_handler(commands=['de'])
def send_welcome(message):
    match = re.search(r'/de\s*(.*)', message.text)
    text = message.text
    if match:
        text = match.group(1)
    if not text:
        bot.reply_to(message, '把上一条消息解密')
        send_welcome(message.reply_to_message)
        return
    
    text = decrypt_message(text)
    bot.reply_to(message, text)
    return


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    message.text = encrypt_message(message.text)
    en_message = message.text
    bot.reply_to(message, message.text)


def start_program():
    end_time = datetime.now()+timedelta(seconds=runtime)
    formatted_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    start_message = log_message(f'服务已启动\n并预计{formatted_time}结束本次服务！')
    bot.send_message(my_chat_id, start_message)
    print(start_message)


start_program()

# 因为是github action执行，所以定时停止
timer = threading.Timer(runtime, exit_program)
timer.start()
bot.polling()

print('本次服务已结束')
sys.exit(0)
