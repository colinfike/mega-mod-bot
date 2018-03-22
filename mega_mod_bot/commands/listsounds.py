# -*- coding: utf-8 -*-
"""
This module is responsible for listing the available soundclips.

This will be refactored into a single sound command that handles all of this.

Command Format:
$listsounds

Sample listsounds command:
`$listsounds`
"""
import re

import boto3

import constants
from namedtuples import ResponseTuple

s3 = boto3.resource('s3')


def execute_command(tokens):
    """Return a ResponseTuple with a list of available sounds."""
    available_sounds = [re.sub('\..+', '', file_name.key) 
                        for file_name
                        in s3.Bucket(constants.SOUND_BUCKET).objects.all()]
    return ResponseTuple(
        message="Available sounds are: " + ', '.join(available_sounds),
        message_format=constants.TEXT_FORMAT,
    )
