# -*- coding: utf-8 -*-
"""
This module is a simple config module for global constants used in the bot.
"""
import os

AUDIO_FORMAT = 'audio'
BANNED_IMAGES = ['known_people/Jon Wakely.png', 'known_people/Jon Fancy.jpg']
BANNED_STRINGS = ['jon', 'wakeley', 'jonathan', 'wakely', 'wakefest', 'john',
                  'jawn', 'jun', 'wukley', ]
COMMAND_SYMBOL = '$'
DOWNLOAD_LOCATION = 'sound_clips/'
ENCODING_BUCKET = 'mega-mod-bot.face-encodings'
IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', ]
MEGA_MOD_BOT_ID = os.environ['MEGA_MOD_BOT_ID']
SOUND_BUCKET = 'mega-mod-bot.sound-clips'
SOUND_DIRECTORY = './sound_clips/'
SOUND_EXTENSION = '.wav'
TEXT_FORMAT = 'text'
DEFAULT_TTD = 5
TOKEN = os.environ['TOKEN']
URL_REGEX = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F]'
             '[0-9a-fA-F]))+')
