# -*- coding: utf-8 -*-
"""
This module is responsible for the playsound command.

The main functionality of this module will involve playing a soundclip into a
specific channel. This may be refactored out even today to combine the sound
related commands into a single parent command.

Command Format:
$playsound <clip_name> 

Sample Ripsound command:
`$playsound perfect_line`

"""
from collections import namedtuple
import os
import re

SOUND_EXTENSION = '.wav'
SOUND_DIRECTORY = './sound_clips/'
AUDIO_FORMAT = 'audio'
MESSAGE_FORMAT = 'message'

ResponseTuple = namedtuple('ResponseTuple', 'message message_format')


def execute_playsound(tokens):
    """Interface for the playsound module."""
    sound_name = tokens[1]
    sound_clips = [re.sub('\..+', '', file_name) 
                   for file_name in os.listdir(SOUND_DIRECTORY)]

    if sound_name in sound_clips:
        sound_path = SOUND_DIRECTORY + sound_name + SOUND_EXTENSION
        return ResponseTuple(
            message=sound_path,
            message_format=AUDIO_FORMAT
        )
    else:
        return ResponseTuple(
            message='Sound not found.',
            message_format=MESSAGE_FORMAT
        )
