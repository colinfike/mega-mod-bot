import asyncio
import discord
import face_recognition
import json
import logging
import re
import requests
import shutil
import sys

from PIL import Image
from io import BytesIO


logging.basicConfig(level=logging.INFO)
client = discord.Client()

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')


TOKEN = '<REDACTED>'
MEGA_MOD_BOT_ID = '<REDACTED>'
BANNED_STRINGS = ['jon', 'wakeley','jonathan', 'wakely', 'wakefest', 'john', 'jawn', 'jun', 'wukley' ]
BANNED_IMAGES = ['known_people/Jon Wakely.png', 'known_people/Jon Fancy.jpg']
IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', ]
URL_REGEX = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
SOUND_PATH = 'sound_clips'
SOUND_CLIPS = {
    'desync and lag': 'desync-and-lag.mp3',
    'getting real close': 'getting-real-close.mp3',
    'two time': 'two-time.mp3',
}

@client.event
async def on_ready():
    '''Prints that the bot has readied up'''
    print('Logged in as MegaModBot')
    print('Opus Loaded:', discord.opus.is_loaded())


@client.event
async def on_message(message):
    '''Parse each message for any banned content.'''
    print(message.content)

    if message.author.id == MEGA_MOD_BOT_ID:
        return False

    channel = message.channel
    if contains_banned_string(message):
        await censor_message(message, channel)
    elif message.attachments:
        for attachment in message.attachments:
            if process_url(attachment['url']):
                await censor_message(message, channel)
    else:
        await detect_sound_clips(message)
        urls = parse_urls(message)
        for url in urls:
            if process_url(url):
                await censor_message(message, channel)


async def censor_message(message, channel):
    '''Deletes a banned message and send's a response to the channel'''
    await client.send_message(channel, 'banned content')
    await client.delete_message(message)
    try:
        await play_audio_for_user(message, 'sound_clips/banned-content.mp3')
    except:
        print('voice failed')


def process_url(url):
    '''Tests if a URL contains an image and if it's a banned image'''
    print(is_image(url))
    try:
        if is_image(url) and is_banned_image(url):
            return True
    except:
        print('Face Recognition Failed')

    return False


def contains_banned_string(message):
    '''Checks a string if it contains one of several banned strings.'''
    return any(banned_string in message.content.lower() for banned_string in BANNED_STRINGS)


def is_image(url):
    '''Makes a HEAD request to get the content-type of the content at the url.'''
    response = requests.head(url)
    print(response.headers['Content-Type'])
    return response.headers['Content-Type'] in IMAGE_TYPES


def parse_urls(message):
    '''Parse all URLs out of any message for testing.'''
    return re.findall(URL_REGEX, message.content)


def is_banned_image(url):
    '''Processes the image to see if it contains any banned faces.'''
    response = requests.get(url, stream=True)
    with open('temp_img.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    banned_encodings = []

    for banned_image in BANNED_IMAGES:
        converted_image = face_recognition.load_image_file(banned_image)
        for encoding in face_recognition.face_encodings(converted_image):
            banned_encodings.append(encoding)

    suspect_image = face_recognition.load_image_file('temp_img.png')
    for suspect_encoding in face_recognition.face_encodings(suspect_image):
        print('Found a face')
        results = face_recognition.compare_faces(banned_encodings, suspect_encoding)
        if (any(results)):
            return True

    return False


async def detect_sound_clips(message):
    '''Checks if any keywords exist in the message and play correspond clip.'''
    keys = SOUND_CLIPS.keys()
    for key in keys:
        if key in message.content.lower():
            try:
                await play_audio_for_user(message, SOUND_PATH + '/' + SOUND_CLIPS[key])
            except:
                print('voice failed')


async def play_audio_for_user(message, audio_clip):
    '''Joins a users channel and plays them an audio clip.'''
    voice = await client.join_voice_channel(message.author.voice.voice_channel)
    player = voice.create_ffmpeg_player(audio_clip, use_avconv=True)
    player.start()
    while not player.is_done():
        await asyncio.sleep(1)
    await voice.disconnect()  


client.run(TOKEN)