# -*- coding: utf-8 -*-
"""
This is the primary module for mega_mod_bot.

It's primary function is to parse all messages, identify ones that are relevant
to mega_mod_bot and dispatch them accordingly. It handles all text and voice
responses as well. This is the bot's main interface.
"""
import asyncio
from importlib import import_module
import logging

import discord

from censor import contains_banned_content
import constants
from exceptions import InvalidCommandException

MODULE_PATH = 'commands.'

logging.basicConfig(level=logging.INFO)
client = discord.Client()

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')


@client.event
async def on_ready():
    """Print that the bot has readied up."""
    print('Logged in as MegaModBot')
    print('Opus Loaded:', discord.opus.is_loaded())


@client.event
async def on_message(message):
    """Parse incoming messages and dispatch them accordingly."""
    print(message.content)

    if message.author.id == constants.MEGA_MOD_BOT_ID:
        return None

    if message.content.startswith(constants.COMMAND_SYMBOL):
        await execute_command(message)
    else:
        await remove_banned_content(message)


async def remove_banned_content(message):
    """Remove any banned content in the message."""
    if (contains_banned_content(message)):
        await remove_message(message)
        await send_message(message, 'banned content', time_to_delete=constants.DEFAULT_TTD)


async def execute_command(message):
    """
    Tokenize and execute command string.

    This will try to import the module with the same name as the command
    and if it exists will call the execute_command function in it. This enables
    a very extensible structure where you can add new commands without
    having to change anything else in the bot.
    """
    tokens = message.content[1:].split(' ')
    command = tokens[0]

    try:
        command_module = import_module(MODULE_PATH + command)
        result = command_module.execute_command(tokens)
    except InvalidCommandException:
        await send_message(message, 'Invalid Command')
    except ModuleNotFoundError:
        await send_message(message, 'Invalid Command')
    else:
        if result.message_format == constants.TEXT_FORMAT:
            await send_message(message, result.message)
        elif result.message_format == constants.AUDIO_FORMAT:
            await send_audio(message, result.message)

        await remove_message(message)


async def send_message(message, message_string, time_to_delete=None):
    """Send passed message to server."""
    sent_message = await client.send_message(message.channel, message_string)
    if time_to_delete:
        await asyncio.sleep(time_to_delete)
        await remove_message(sent_message)


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
    client.run(constants.TOKEN)
