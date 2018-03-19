# -*- coding: utf-8 -*-
"""
This is the primary module for mega_mod_bot.

It's primary function is to parse all messages, identify ones that are relevant
to mega_mod_bot and dispatch them accordingly. It handles all text and voice
responses as well. This is the bot's main interface.

TODO:
1) Implement list, play, and save Audio Clips.
2) Update command parsing.
3) Add caching on downloaded youtube videos.
4) Update ripsound so it doesn't block.
"""

import asyncio
import discord
import logging
import os

from censor import contains_banned_content
from commands.ripsound import execute_ripsound
from commands.playsound import execute_playsound
from commands.listsounds import execute_listsounds


logging.basicConfig(level=logging.INFO)
client = discord.Client()

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

TOKEN = os.environ['TOKEN']
MEGA_MOD_BOT_ID = os.environ['MEGA_MOD_BOT_ID']
COMMAND_SYMBOL = '$'
AUDIO_FORMAT = 'audio'
MESSAGE_FORMAT = 'message'


@client.event
async def on_ready():
    """Print that the bot has readied up."""
    print('Logged in as MegaModBot')
    print('Opus Loaded:', discord.opus.is_loaded())


@client.event
async def on_message(message):
    """Parse incoming messages and dispatch them accordingly."""
    print(message.content)

    if message.author.id == MEGA_MOD_BOT_ID:
        return None

    if message.content.startswith(COMMAND_SYMBOL):
        await execute_command(message)
    else:
        await remove_banned_content(message)


async def remove_banned_content(message):
    """Remove any banned content in the message."""
    if (contains_banned_content(message)):
        await send_message(message, 'banned content')
        await remove_message(message)


async def execute_command(message):
    """Tokenize and execute command string."""
    tokens = message.content[1:].split(' ')
    # TODO: Automatically do this by pulling command names from the command dir
    # TODO: Add error handling on invalid command
    # TODO: Returning a tuple can help us figure out if we need to send a text
    #       or voice message while keeping this module as the main text/voice
    #       bus.
    if (tokens[0] == 'ripsound'):
        result = execute_ripsound(tokens)
    elif (tokens[0] == 'playsound'):
        result = execute_playsound(tokens)
    elif (tokens[0] == 'listsounds'):
        result = execute_listsounds(tokens)

    if result.message_format == MESSAGE_FORMAT:
        await send_message(message, result.message)
    elif result.message_format == AUDIO_FORMAT:
        await send_audio(message, result.message)


async def send_message(message, message_string):
    """Send passed message to server."""
    await client.send_message(message, message_string)


async def remove_message(message):
    """Remove passed in message from server."""
    await client.delete_message(message)


async def send_audio(message, audio_clip):
    """Play audio clip in specified voice channel."""
    voice = await client.join_voice_channel(message.author.voice.voice_channel)
    player = voice.create_ffmpeg_player(audio_clip, use_avconv=True)
    player.start()
    while not player.is_done():
        await asyncio.sleep(1)
    await voice.disconnect()

if __name__ == '__main__':
    client.run(TOKEN)
