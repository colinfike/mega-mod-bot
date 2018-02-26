# -*- coding: utf-8 -*-
"""
This module handles checking messages for banned content.

This includes strings, images, and image urls.
"""

import face_recognition
import re
import requests
import shutil
import tempfile


BANNED_IMAGES = ['known_people/Jon Wakely.png', 'known_people/Jon Fancy.jpg']
IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', ]
URL_REGEX = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F]'
             '[0-9a-fA-F]))+')
BANNED_STRINGS = ['jon', 'wakeley', 'jonathan', 'wakely', 'wakefest', 'john',
                  'jawn', 'jun', 'wukley', ]


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
    return re.findall(URL_REGEX, message.content)


def contains_banned_string(message):
    """Check if a string contains any banned substrings."""
    return any(banned_string in message.content.lower()
               for banned_string in BANNED_STRINGS)


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


def is_image(url):
    """Make a HEAD request to get the content-type of the URL's content."""
    response = requests.head(url)
    return response.headers['Content-Type'] in IMAGE_TYPES


def is_banned_image(url):
    """Process the image to see if it contains any banned faces."""
    response = requests.get(url, stream=True)
    temp_file = tempfile.TemporaryFile()
    shutil.copyfileobj(response.raw, temp_file)

    banned_encodings = []
    for banned_image in BANNED_IMAGES:
        converted_image = face_recognition.load_image_file(banned_image)
        for encoding in face_recognition.face_encodings(converted_image):
            banned_encodings.append(encoding)

    suspect_image = face_recognition.load_image_file(temp_file)
    for suspect_encoding in face_recognition.face_encodings(suspect_image):
        results = face_recognition.compare_faces(
            banned_encodings, suspect_encoding)
        if (any(results)):
            return True

    return False
