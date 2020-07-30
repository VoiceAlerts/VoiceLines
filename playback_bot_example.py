from pprint import pprint
from obswebsocket import obsws, requests
from shutil import copyfile
from twitchio.ext import commands
from playsound import playsound
import subprocess
import os
import zmq
import sys
import time
import logging
import pyautogui
import shutil
import threading, queue

sound_queue = queue.Queue()

def sound_worker():
    while True:
        item = sound_queue.get()
        print(f'Playing {item}')
        playsound('C:\\Videos\\voicelines\\'+str(item)+'.mp3', True)
        print(f'Finished {item}')
        sound_queue.task_done()

# turn-on the worker thread
threading.Thread(target=sound_worker, daemon=True).start()


my_channel = "obs-control"

host = "localhost"
port = 4444
password = "secret"
ws = obsws(host, port, password)
ws.connect()

last_clip_playback = time.time()
last_sound_playback = time.time()

clips = os.listdir('C:\\Videos\\clips')
clip_titles = []
for clip in clips:
    clip_titles.append(clip.lower().replace('.mp4',''))

voicelines = os.listdir('C:\\Videos\\voicelines')
voiceline_titles = []
for voiceline in voicelines:
    voiceline_titles.append(voiceline.lower().replace('.mp3',''))

#SetSceneItemProperties

def change_scene(name):
    ws.call(requests.SetCurrentScene(name))   

def start_stream():
    ws.call(requests.StartStreaming())

def stop_stream():
    ws.call(requests.StopStreaming())

def del_file(x):
    try:
        os.remove(str(x))
    except Exception:
        pass

def copy_file(x, y):
    try:
        shutil.copy2(str(x), str(y)) #y-> target
    except Exception:
        pass

def play_clip(name):
    ws.call(requests.SetSceneItemProperties(item='clip',visible=False))
    time.sleep(0.2)
    del_file('C:\\Videos\\clip.mp4')
    copy_file('C:\\Videos\\clips\\'+name+'.mp4' , 'C:\\Videos\\clip.mp4')
    time.sleep(0.2)
    ws.call(requests.SetSceneItemProperties(item='clip',visible=True))

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(irc_token='oauth:YOUROAUTH', client_id='jzkbprff40iqj646a697cyrvl0zt2m6', nick='YourBotNick', prefix='!',
                         initial_channels=['#yourchannel'])
                         
                         
    async def event_message(self, message):
        global last_sound_playback, last_clip_playback, sound_queue
        msg_str = time.strftime("[%H:%M:%S] ", time.localtime()) + str(message.author.name) + ": " + message.content
        print(msg_str + " @ " + str(message.channel))
        found = False
        for voiceline in voiceline_titles:
            if message.content.lower() == ("!"+str(voiceline)):
                if time.time() - last_sound_playback >= 3.:
                    last_sound_playback = time.time()
                    sound_queue.put(str(voiceline))
        for clip in clip_titles:
            if message.content.lower() == ("!"+str(clip)):
                if time.time() - last_clip_playback >= 30.:
                    last_clip_playback = time.time()
                    play_clip(str(clip))



bot = Bot()
bot.run()