# -*- coding: utf-8 -*-
"""
This module handles checking messages for banned content.

This includes strings, images, and image urls.
"""
import boto3
import re
import shutil
import tempfile

import face_recognition
import numpy
import requests
from utils import is_image

import constants

banned_images = []
s3 = boto3.resource('s3')


def contains_banned_content(message):
    """Return if message contains banned content."""
    if contains_banned_string(message):
        return True

    if contains_banned_attachment(message):
        return True

    if contains_banned_url(message):
        return True

    return False


def parse_urls(message):
    """Return all urls for in the message."""
    return re.findall(constants.URL_REGEX, message.content)


def contains_banned_string(message):
    """Check if a string contains any banned substrings."""
    return any(banned_string in message.content.lower()
               for banned_string in constants.BANNED_STRINGS)


def contains_banned_attachment(message):
    """Return if a message contains an attachment with banned content."""
    return any(attachment for attachment in message.attachments
               if inspect_url(attachment['url']))


def contains_banned_url(message):
    """Return if a url contains a url with banned content."""
    return any(url for url in parse_urls(message) if inspect_url(url))


def inspect_url(url):
    """Test if a URL contains an image and if it's a banned image."""
    if is_image(url) and is_banned_image(url):
        return True

    return False


def is_banned_image(url):
    """Process the image to see if it contains any banned faces."""
    response = requests.get(url, stream=True)
    temp_file = tempfile.TemporaryFile()
    shutil.copyfileobj(response.raw, temp_file)

    suspect_image = face_recognition.load_image_file(temp_file)
    for suspect_encoding in face_recognition.face_encodings(suspect_image):
        results = face_recognition.compare_faces(banned_images,
                                                 suspect_encoding)
        if (any(results)):
            return True

    return False


def append_new_encoding(encoding):
    """Append new face encoding into in-memory storage."""
    banned_images.append(encoding)


def load_banned_images():
    """Load any face encodings from S3 into memory."""
    bucket = s3.Bucket(constants.ENCODING_BUCKET)
    for file in bucket.objects.all():
        with tempfile.TemporaryFile() as temp_file:
            bucket.download_fileobj(file.key, temp_file)
            temp_file.seek(0)
            append_new_encoding(numpy.load(temp_file))
