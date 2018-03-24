# -*- coding: utf-8 -*-
"""
This module handles adding images to the banned image collection.

We take the image, process it into the mapping that face recognition package
uses, saves the resulting ndarray to file and uploads it to S3.

NOTE: At this time only links to images are supported.

Command Format:
$addbannedimage <link_to_image>

Sample Ripsound command:
$addbannedimage http://coolimagehoster.com/9XaZ12Lanz
"""
from uuid import uuid4
from tempfile import TemporaryFile
import shutil

import boto3
from face_recognition import face_encodings, load_image_file
from numpy import save
import requests

from censor import append_new_encoding
import constants
from exceptions import InvalidCommandException
from namedtuples import ResponseTuple
from utils import is_image

s3 = boto3.resource('s3')


def execute_command(tokens):
    """Responsible for executing the addbannedimage command."""
    # ToDo: Pull this all out into a util method that returns a FLO.
    # Will also use iter_Content to auto decode deflate/gzip
    # TODO: Break some of this shit out a bit maybe?
    image_url = tokens[1]
    if not is_image(image_url):
        raise InvalidCommandException

    response = requests.get(image_url, stream=True)
    temp_file = TemporaryFile()
    shutil.copyfileobj(response.raw, temp_file)

    image_file = load_image_file(temp_file)
    for encoding in face_encodings(image_file):
        append_new_encoding(encoding)
        with TemporaryFile() as temp_file:
            save(temp_file, encoding)
            temp_file.seek(0)
            s3.meta.client.upload_fileobj(temp_file, constants.ENCODING_BUCKET,
                                          uuid4().hex + '.npy')

    return ResponseTuple(
        message='Image added to ban list.',
        message_format=constants.TEXT_FORMAT,
    )
