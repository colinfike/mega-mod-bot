# -*- coding: utf-8 -*-
"""
This module is responsible for the ripsound command.

The main functionality of this module will involve fetching youtube videos,
ripping the sound from the videos, isolating a specific part of the audio
and save it for playback in the future.

Command Format:
$ripsound <clip_name> <youtube_URL> <start_time_seconds> <end_time_seconds>

Sample Ripsound command:
`$ripsound perfect_line https://www.youtube.com/watch?v=oYmqJl4MoNI 84 89`

TODO:
    1) Add overwrite protection.
    2) Persist file names once we use some persistent storage.
"""
import os
import re

import boto3
from pydub import AudioSegment
import youtube_dl

import constants
from exceptions import InvalidCommandException
from namedtuples import ResponseTuple

s3 = boto3.resource('s3')

RIPSOUND = 'ripsound'
TOKEN_COUNT = 5
SOUND_TIME_LIMIT = 10
URL_REGEX = re.compile('^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|' +
                       'youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)' +
                       '(\S+)?$')


def execute_command(tokens):
    """
    Interface for the ripsound module.
    
    This function downloads the youtube video passed in, converts it, clip the
    audio to the time desired, exports it locally, and uploads it to S3.
    """
    if validate_tokens(tokens):
        raise InvalidCommandException

    clip_name = tokens[1]
    video_url = tokens[2]
    start_time_ms = int(tokens[3]) * 1000
    end_time_ms = int(tokens[4]) * 1000
    save_location = constants.DOWNLOAD_LOCATION + clip_name

    # Need to use %(ext) otherwise ffmpeg bugs out. This uglies things a bit.
    options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': save_location + '.%(ext)s',
    }
    with youtube_dl.YoutubeDL(options) as downloader:
        downloader.download([video_url])

    audio_location = save_location + '.mp3'
    sound_path = trim_and_export_audio(audio_location, clip_name,
                                       start_time_ms,  end_time_ms)
    s3.meta.client.upload_file(sound_path, constants.SOUND_BUCKET,
                               clip_name + constants.SOUND_EXTENSION)
    os.remove(audio_location)
    return ResponseTuple(
        message='Sound clip saved.',
        message_format=constants.TEXT_FORMAT,
    )


def trim_and_export_audio(save_location, clip_name, start_ms, end_ms):
    """Trim and export audio clip locally."""
    full_sound_file = AudioSegment.from_file(save_location, format='mp3')
    audio_location = constants.DOWNLOAD_LOCATION + clip_name + '.wav'
    full_sound_file[start_ms:end_ms].export(audio_location, format='wav')
    return audio_location


def validate_tokens(tokens):
    """Validate tokens for the ripsound command."""
    return any([
        len(tokens) != TOKEN_COUNT,
        not tokens[0].lower() == RIPSOUND,
        not re.match(URL_REGEX, tokens[2]),
        int(tokens[4]) - int(tokens[3]) > SOUND_TIME_LIMIT
    ])
