import os

clips = os.listdir('clips')
clip_titles = []
for clip in clips:
    clip_titles.append(clip.lower().replace('.mp4',''))

voicelines = os.listdir('voicelines')
voiceline_titles = []
for voiceline in voicelines:
    voiceline_titles.append(voiceline.lower().replace('.mp3',''))

voiceline_titles.sort()
clip_titles.sort()

f= open("voicelines.txt","w+")
for voice in voiceline_titles:
    f.write("!"+voice+"\n")
f.close()

f= open("clips.txt","w+")
for clip in clip_titles:
    f.write("!"+clip+"\n")
f.close()