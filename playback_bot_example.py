from pprint import pprint
from obswebsocket import obsws, requests
from shutil import copyfile
from twitchio.ext import commands
from playsound import playsound
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import subprocess
import os
import zmq
import sys
import time
import logging
import pyautogui
import shutil
import threading, queue

play_queue = queue.Queue()

def sound_worker():
    while True:
        item = play_queue.get()
        if item[0]== 'voice':
            print(f'Playing voice {item[1]}')
            try:
                audio_file = 'C:\\Videos\\voicelines\\'+str(item[1])+'.mp3'
                audio = MP3(audio_file)
                playsound(audio_file, False)
                print("Sleeping for: "+str(audio.info.length))
                time.sleep(audio.info.length)
                print(f'Finished {item[1]}')
            except Exception:
                pass
        else:
            print(f'Playing clip {item[1]}')
            try:
                play_clip(str(item[1]))
            except Exception:
                pass
            print(f'Finished {item[1]}')
        play_queue.task_done()


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

with open('C:\\Videos\\blocklist.txt') as f:
    block_lines = f.read().splitlines()

blocklist = list(filter(None, block_lines))
blocklist = [x.lower() for x in blocklist]
clip_titles = [ x for x in clip_titles if x not in blocklist ]
voiceline_titles = [ x for x in voiceline_titles if x not in blocklist ]

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
    clip = MP4('C:\\Videos\\clip.mp4')
    ws.call(requests.SetSceneItemProperties(item='clip',visible=True))
    print("Sleeping for "+str(clip.info.length))
    time.sleep(clip.info.length)
    ws.call(requests.SetSceneItemProperties(item='clip',visible=False))

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(irc_token='oauth:YOUROAUTH', client_id='jzkbprff40iqj646a697cyrvl0zt2m6', nick='YourBotNick', prefix='!',
                         initial_channels=['#yourchannel'])
                         
                         
    async def event_message(self, message):
        global last_sound_playback, last_clip_playback, play_queue
        msg_str = time.strftime("[%H:%M:%S] ", time.localtime()) + str(message.author.name) + ": " + message.content
        print(msg_str + " @ " + str(message.channel))
        found = False
        msg_line = message.content.lower()
        msg_line = msg_line.replace('ß','ss')
        msg_line = msg_line.replace('ä','ae')
        msg_line = msg_line.replace('ü','ue')
        msg_line = msg_line.replace('ö','oe')
        if '!' in msg_line:
            msg_line = msg_line.split()[0]
        msg_line = msg_line.encode('ascii',errors='ignore').decode()
        for voiceline in voiceline_titles:
            if msg_line == ("!"+str(voiceline)):
                if time.time() - last_sound_playback >= 1.:
                    last_sound_playback = time.time()
                    play_queue.put(['voice', str(voiceline)])
        for clip in clip_titles:
            if msg_line == ("!"+str(clip)):
                if time.time() - last_clip_playback >= 120.:
                    last_clip_playback = time.time()
                    play_queue.put(['clip', str(clip)])



bot = Bot()
bot.run()
