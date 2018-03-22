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
import boto3
import os
import re

import constants
from namedtuples import ResponseTuple

s3 = boto3.resource('s3')


def execute_command(tokens):
    """Interface for the playsound module."""
    sound_name = tokens[1]

    if sound_clip_exists(sound_name):
        sound_path = (constants.SOUND_DIRECTORY + sound_name +
                      constants.SOUND_EXTENSION)
        return ResponseTuple(
            message=sound_path,
            message_format=constants.AUDIO_FORMAT
        )
    else:        
        return ResponseTuple(
            message='Sound not found.',
            message_format=constants.TEXT_FORMAT
        )


def audio_exists_locally(sound_name):
    """Return if a sound exists locally."""
    sound_clips = [re.sub('\..+', '', file_name) 
                   for file_name in os.listdir(constants.SOUND_DIRECTORY)]
    return sound_name in sound_clips


def audio_exists_s3(sound_name):
    """Return if a sound exists in S3."""
    sound_bucket = s3.Bucket(constants.SOUND_BUCKET)
    sound_clips = [re.sub('\..+', '', file_name.key) 
                   for file_name in sound_bucket.objects.all()]
    return sound_name in sound_clips


def fetch_from_s3(sound_name):
    """Download sound from S3."""
    sound_name = sound_name + constants.SOUND_EXTENSION
    s3.Bucket(constants.SOUND_BUCKET).download_file(
        Key=sound_name,
        Filename=constants.SOUND_DIRECTORY + sound_name
    )
    return None


def sound_clip_exists(sound_name):
    """
    Return if a sound has already been fetched.
    
    We check if the file exists lcoally and if it does not we check if it
    exists in S3. If it does, we download it locally.
    """
    sound_exists = False
    if audio_exists_locally(sound_name):
        sound_exists = True
    elif audio_exists_s3(sound_name):
        fetch_from_s3(sound_name)
        sound_exists = True
    return sound_exists
