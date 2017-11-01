# -*- coding: utf-8 -*-
"""
This module handles checking messages for banned content.

This includes strings, images, and image urls.
"""
BANNED_STRINGS = ['jon', 'wakeley', 'jonathan', 'wakely', 'wakefest', 'john',
                  'jawn', 'jun', 'wukley', ]


def contains_banned_content(message):
    """Return if message contains banned content."""
    if contains_banned_string(message):
        return True


def contains_banned_string(message):
    """Check if a string contains any banned substrings."""
    return any(banned_string in message.content.lower()
               for banned_string in BANNED_STRINGS)


    #     await censor_message(message, channel)
    # elif message.attachments:
    #     for attachment in message.attachments:
    #         if process_url(attachment['url']):
    #             await censor_message(message, channel)
    # else:
    #     await detect_sound_clips(message)
    #     urls = parse_urls(message)
    #     for url in urls:
    #         if process_url(url):
    #             await censor_message(message, channel)
