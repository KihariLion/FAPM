import re
import time
import urllib.parse
import urllib.request

from . import cli
from .constants import *
from .message import Message


token_a = cli.args.a if cli.args.a and cli.is_session_token(cli.args.a) else None
token_b = cli.args.b if cli.args.b and cli.is_session_token(cli.args.b) else None
folders = tuple(set(cli.args.f)) if cli.args.f else FOLDERS

unread_messages = []


def _get_ids(folder, page):
    print(f'Scanning messages in {folder.title()}, page {page:,}')
    request = urllib.request.Request(f'https://www.furaffinity.net/msg/pms/{page}/')
    request.add_header('Cookie', f'a={token_a}; b={token_b}; folder={folder}')
    request.add_header('Host', 'www.furaffinity.net')
    request.add_header('User-Agent', f'FAPM/{VERSION}')
    html = urllib.request.urlopen(request).read().decode()
    time.sleep(SLEEP)
    unread_messages.extend(int(id_) for id_ in (RE_MODERN_UNREAD.findall(html) or RE_CLASSIC_UNREAD.findall(html)))
    return [int(id_) for id_ in (RE_MODERN_ID.findall(html) or RE_CLASSIC_ID.findall(html))]


def prompt_session_tokens():
    global token_a
    global token_b

    if token_a is None or token_b is None:
        print(ABOUT_COOKIES)

        while not cli.is_session_token(token_a):
            token_a = input(f'UUID for session token A: ').strip()

        while not cli.is_session_token(token_b):
            token_b = input(f'UUID for session token B: ').strip()

        print()


def message_index():
    message_index = {}

    for folder in folders:
        page = 1
        message_ids = _get_ids(folder, page)

        while message_ids:
            message_index.update((id_, folder) for id_ in message_ids)
            page += 1
            message_ids = _get_ids(folder, page)

    return message_index


def get_message(id_, folder):
    request = urllib.request.Request(f'https://www.furaffinity.net/viewmessage/{id_}/')
    request.add_header('Cookie', f'a={token_a}; b={token_b}; folder={folder}')
    request.add_header('Host', 'www.furaffinity.net')
    request.add_header('User-Agent', f'FAPM/{VERSION}')
    html = urllib.request.urlopen(request).read().decode()
    time.sleep(SLEEP)
    return Message(html=html, id_=id_, folder=folder)


# The folder parameter is probably not necessary, but more research is needed.
# For now, call this function for each folder that contains unread messages,
# and only for messages that were received by the user.
def mark_unread(ids, folder):
    data = [('manage_notes', 1), ('move_to', 'unread')]
    data.extend(('items[]', id_) for id_ in ids)
    request = urllib.request.Request(f'https://www.furaffinity.net/msg/pms/', data=urllib.parse.urlencode(data).encode())
    request.add_header('Cookie', f'a={token_a}; b={token_b}; folder={folder}')
    request.add_header('Host', 'www.furaffinity.net')
    request.add_header('User-Agent', f'FAPM/{VERSION}')
    urllib.request.urlopen(request)
    time.sleep(SLEEP)
