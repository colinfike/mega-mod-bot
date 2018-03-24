# -*- coding: utf-8 -*-
"""This module holds any utility methods shared across modules."""
import requests

import constants


def is_image(url):
    """Make a HEAD request to get the content-type of the URL's content."""
    response = requests.head(url)
    return response.headers['Content-Type'] in constants.IMAGE_TYPES
