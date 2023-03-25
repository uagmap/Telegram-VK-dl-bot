#this file is responsible for bot operation (commands, scheduled delivery of message)

import reddit
import telebot
import os
import schedule
import requests
from bs4 import BeautifulSoup
from replit import db
from threading import Thread
from time import sleep
from keep_alive import keep_alive
from pytube import YouTube
import yt_dlp

teleToken = os.environ['TOKEN']
bot = telebot.TeleBot(teleToken)

#qotd = reddit.get_qotd() + "\n\n" + reddit.qotd_trans()
#print(reddit.get_qotd() + "\n\n" + reddit.qotd_trans())


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def send_vopros():
    for chatName in db.keys():
        try:
            bot.send_message(
                db[chatName],
                reddit.get_qotd())  # + "\n\n" + reddit.qotd_trans())
        except:
            pass


def download_video(url):
    if 'youtube.com' in url:
        # Create a YouTube object with the video URL
        yt = YouTube(url)

        # Get the first stream (i.e., the highest resolution)
        stream = yt.streams.get_highest_resolution()

        #if file exists then delete and overwrite
        if os.path.exists("video.mp4"):
            os.remove("video.mp4")

        # Download the video
        stream.download(filename="video.mp4")

        # Return the path to the downloaded video file
        return "video.mp4"

    elif 'vk.com' in url:
        #if the video is vk video then it will be parsed
        #send a get request to the video page
        response = requests.get(url)

        #parse the response with bs
        soup = BeautifulSoup(response.text, 'html.parser')

        #now the task is to find the video file link, which is stored in embedUrl tag
        embedUrl_tag = soup.find('link', itemprop='embedUrl')

        #extract the link from the tag
        embed_url = embedUrl_tag['href']

        ytdl = yt_dlp.YoutubeDL({'outtmpl': 'video.mp4'})
        if os.path.exists('video.mp4'):
            os.remove('video.mp4')
        ytdl.download([embed_url])

        #convert the video so that its supported by telegram player (error is fine)
        os.system("ffmpeg -i video.mkv -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k -movflags +faststart video.mp4")

        return 'video.mp4'


schedule.every().day.at("09:00").do(send_vopros)  #replit timezone -3 from mine

Thread(target=schedule_checker).start()
keep_alive()


@bot.message_handler(commands=['start'])
def start(message):
    chat_name = str(message.chat.title)
    if chat_name not in db.keys():
        db[chat_name] = message.chat.id
        bot.send_message(message.chat.id, "Чат добавлен в рассылку")
    else:
        bot.send_message(message.chat.id, "Уже выполнено")


@bot.message_handler(commands=['stop'])
def stop(message):
    chat_name = str(message.chat.title)
    if chat_name in db.keys():
        del db[chat_name]
        bot.send_message(message.chat.id, "Чат убран из рассылки")
    else:
        bot.send_message(message.chat.id, "Чат не в рассылке")


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id,
        "Каждый день я буду задавать вопрос с \nr/AskReddit\n А еще я могу скачать видео с вк и ютуб\nКоманды:\n/start - добавить чат в рассылку вопроса дня.\n/vopros - показать вопрос дня.\n/help - показать это сообщение."
    )


@bot.message_handler(commands=['vopros'])
def vopros(message):
    #bot.send_message(message.chat.id, reddit.get_qotd() + "\n\n" + reddit.qotd_trans()) это с переводом
    bot.send_message(message.chat.id, reddit.get_qotd())


#if message received is just text
@bot.message_handler(content_types=['text'])
def handle_message(message):
    if message.text.lower() == "да":
        bot.reply_to(message, "Пизда")

      #check if the message contains a link
  if 'youtube.com' in message.text or 'vk.com' in message.text:
    # Download the video and get the path to the downloaded file
    try:
      video_path = download_video(message.text)

      #send the downloaded video back to the user
      with open(video_path, 'rb') as f:
        bot.send_video(message.chat.id, f, supports_streaming=True)
    except yt_dlp.utils.DownloadError:
      bot.reply_to(message, "Видео защищено настройками приватности :с")


bot.polling(none_stop=True, interval=0)

#sometimes replit autoupdates packages and installs wrong package, this is fix:
#pip3 uninstall telebot
#pip3 uninstall PyTelegramBotAPI
#pip3 install pyTelegramBotAPI
#pip3 install --upgrade pyTelegramBotAPI

#pip install googletrans==4.0.0-rc1
