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

import youtube_dl
import os

from collections import namedtuple
from pydub import AudioSegment

MESSAGE_FORMAT = 'message'
DOWNLOAD_LOCATION = 'sound_clips/'
ResponseTuple = namedtuple('ResponseTuple', 'message message_format')


def execute_ripsound(tokens):
    """Interface for the ripsound module."""
    # TODO: Put in validation of the tokens.
    clip_name = tokens[1]
    video_url = tokens[2]
    start_time_ms = int(tokens[3]) * 1000
    end_time_ms = int(tokens[4]) * 1000
    save_location = DOWNLOAD_LOCATION + clip_name

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
    trim_and_export_audio(audio_location, clip_name, start_time_ms,
                          end_time_ms)
    os.remove(audio_location)
    return ResponseTuple(
        message='Sound clip save.',
        message_format=MESSAGE_FORMAT,
    )


def trim_and_export_audio(save_location, clip_name, start_ms, end_ms):
    """Trim and export audio clip."""
    temp_sound_file = AudioSegment.from_file(save_location, format='mp3')
    file_location = DOWNLOAD_LOCATION + clip_name + '.wav'
    return temp_sound_file[start_ms:end_ms].export(file_location, format='wav')
