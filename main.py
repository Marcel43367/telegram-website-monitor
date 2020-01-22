#!/usr/bin/env python
import sys
sys.path.append('settings')
from telegram.ext import Updater, CommandHandler
from settings import TELEGRAM_API_KEY, CHECK_INTERVAL, MSG_THRESHOLD
from data import Website
import requests
from decorators import required_argument, valid_url
import datetime
import time
import telegram


help_text = """
The bot ensures that your website is always online. In the case of unavailability for more than 5 minutes, the bot will send you a message.

Commands:

/help - Help
/list - Show your added urls
/add <url> - Add new url for monitoring
/del <url> - Remove existing url
/test <url> - Test current status code for url right now

Url format is http[s]://host.zone/path?querystring
For example:

/test https://example.com
"""

lastCall = datetime.datetime.now()

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Hello!\nThis is telegram bot to check that the site is alive.\n%s" % help_text)


def show_help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="%s" % help_text)


@required_argument
@valid_url
def add(bot, update, args):
    print('add')
    print(args[0])
    url = args[0].lower()
    print(url)
    website_count = (Website.select().where((Website.chat_id == update.message.chat_id) & (Website.url == url)).count())
    print(website_count)
    if website_count == 0:
        website = Website(chat_id=update.message.chat_id, url=url)
        print('ok1')
        website.save(force_insert=True)
        print('ok2')
        bot.sendMessage(chat_id=update.message.chat_id, text="Added %s" % url)
        print('ok3')
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Website %s already exists" % url)
    print('end')


@required_argument
def delete(bot, update, args):
    url = args[0].lower()
    website = Website.get((Website.chat_id == update.message.chat_id) & (Website.url == url))
    if website:
        website.delete_instance()
        bot.sendMessage(chat_id=update.message.chat_id, text="Deleted %s" % url)
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Website %s is not exists" % url)


def url_list(bot, update):
    websites = (Website.select().where(Website.chat_id == update.message.chat_id))
    out = ''
    for website in websites:
        out += "%s\n- last checked: %s\n- status code: %s\n- last seen: %s\n\n" % (website.url, website.last_checked.strftime("%Y-%m-%d %H:%M:%S"), website.last_status_code, website.last_seen.strftime("%Y-%m-%d %H:%M:%S"))
    if out == '':
        bot.sendMessage(chat_id=update.message.chat_id, text="List empty")
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="%s" % out)


@required_argument
@valid_url
def test(bot, update, args):
    url = args[0].lower()
    try:
        r = requests.head(url)
        if r.status_code == 200:
            bot.sendMessage(chat_id=update.message.chat_id, text="Url %s is alive (status code 200)" % url)
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text="Status code of url %s is %s" % (url, r.status_code))
    except:
        bot.sendMessage(chat_id=update.message.chat_id, text="Error for url %s" % url)

# check availability for all websites
def check():
    websites = (Website.select())
    bot = telegram.Bot(token=TELEGRAM_API_KEY)
    for website in websites:
        url = website.url
        print("Requesting availability for %s" %(url))
        try:
            r = requests.head(url)
            status_code = r.status_code
            if r.status_code == 200:
                website.last_seen = datetime.datetime.now()
                website.msg_send = 0
        except:
            status_code = 0
        print("Status Code %s\n" %(status_code))
        website.last_status_code = status_code
        website.last_checked = datetime.datetime.now()
        if status_code != 200:
            if (datetime.datetime.now() > website.last_seen + datetime.timedelta(seconds = MSG_THRESHOLD)) and (website.msg_send == 0): 
                website.msg_send = 1
                bot.sendMessage(chat_id=website.chat_id,text="**Website:**\n- %s\n- not available for %s seconds.\n- Last seen %s" % (url, MSG_THRESHOLD,website.last_seen.strftime("%Y-%m-%d %H:%M:%S")))

        website.save()

## MAIN
updater = Updater(TELEGRAM_API_KEY)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler("add", add, pass_args=True))
updater.dispatcher.add_handler(CommandHandler("del", delete, pass_args=True))
updater.dispatcher.add_handler(CommandHandler("list", url_list))
updater.dispatcher.add_handler(CommandHandler("test", test, pass_args=True))
updater.dispatcher.add_handler(CommandHandler("help", show_help))

print('Telegram bot started\n')
updater.start_polling(poll_interval = 1)

while True:
    if (datetime.datetime.now() > lastCall + datetime.timedelta(seconds = CHECK_INTERVAL)): 
        lastCall = datetime.datetime.now()
        check()
    time.sleep(1)
    
