# -*- coding: utf-8 -*-
"""
This is the primary module for mega-mod-bot.

It's primary function is to parse all messages, identify ones that are relevant
to mega-mod-bot and dispatch them accordingly. It handles all text and voice
responses as well. This is the bot's main interface.
"""

import discord
import logging
import os
from censor import contains_banned_content
from commands.ripsound import execute_ripsound


logging.basicConfig(level=logging.INFO)
client = discord.Client()

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

TOKEN = os.environ['TOKEN']
MEGA_MOD_BOT_ID = os.environ['MEGA_MOD_BOT_ID']
COMMAND_SYMBOL = '$'


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
        execute_command(message)
    else:
        await remove_banned_content(message)


async def remove_banned_content(message):
    """Remove any banned content in the message."""
    if (contains_banned_content(message)):
        await send_message(message.channel, 'banned content')
        await remove_message(message)


def execute_command(message):
    """Tokenize and execute command string."""
    tokens = message.content[1:].split(' ')
    # TODO: Automatically do this by pulling command names from the command dir
    # TODO: Add error handling on invalid command
    # TODO: Returning a tuple can help us figure out if we need to send a text
    #       or voice message while keeping this module as the main text/voice
    #       bus.
    if (tokens[0] == 'ripsound'):
        execute_ripsound(tokens)


async def send_message(channel, message_string):
    """Send passed message to server."""
    await client.send_message(channel, message_string)


async def remove_message(message):
    """Remove passed in message from server."""
    await client.delete_message(message)


client.run(TOKEN)
