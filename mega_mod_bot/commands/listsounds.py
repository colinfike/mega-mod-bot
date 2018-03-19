# -*- coding: utf-8 -*-
"""
This module is responsible for listing the available soundclips.

This will be refactored into a single sound command that handles all of this.

Command Format:
$listsounds

Sample listsounds command:
`$listsounds`
"""
import os
import re

from collections import namedtuple

AUDIO_FORMAT = 'audio'
MESSAGE_FORMAT = 'message'
SOUND_DIRECTORY = './sound_clips/'
ResponseTuple = namedtuple('ResponseTuple', 'message message_format')


def execute_listsounds(tokens):
    """Return a ResponseTuple with a list of available sounds."""
    available_sounds = [re.sub('\..+', '', file_name) 
                        for file_name in os.listdir(SOUND_DIRECTORY)]
    return ResponseTuple(
        message="Available sounds are: " + ', '.join(available_sounds),
        message_format=MESSAGE_FORMAT,
    )
