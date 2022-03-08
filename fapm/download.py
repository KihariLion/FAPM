import re
import time
import urllib.parse
import urllib.request

from . import cli
from .constants import *
from .message import Message


def is_uuid(value):
    return isinstance(value, str) and RE_UUID.match(value)


token_a = cli.args.a if is_uuid(cli.args.a) else None
token_b = cli.args.b if is_uuid(cli.args.b) else None
unread_messages = []


def prompt_session_tokens():
    global token_a
    global token_b

    if token_a is None or token_b is None:
        print(ABOUT_COOKIES)

        while not is_uuid(token_a):
            token_a = input(f'UUID for session token A: ').strip()

        while not is_uuid(token_b):
            token_b = input(f'UUID for session token B: ').strip()

        print()


def http_request(url, headers=None, data=None, html=False):
    if data:
        data = urllib.parse.urlencode(data).encode()

    request = urllib.request.Request(url, data=data)
    request.add_header('Host', 'www.furaffinity.net')
    request.add_header('User-Agent', f'FAPM/{VERSION}')

    if headers:
        for name, value in headers.items():
            request.add_header(name, value)

    for attempt in range(HTTP_ATTEMPTS + 1):
        if attempt == HTTP_ATTEMPTS:
            cli.die('HTTP exception limit reached')

        try:
            response = urllib.request.urlopen(request)
        except:
            cli.warn('HTTP exception raised, waiting to retry')
            time.sleep(30)
        else:
            break

    time.sleep(HTTP_SLEEP)
    return response.read().decode() if html else response


def get_online_index():
    online_index = {}
    folders = tuple(set(cli.args.f)) if cli.args.f else FOLDERS

    for folder in folders:
        headers = {'Cookie': f'a={token_a}; b={token_b}; folder={folder}'}
        page = 1

        while cli.args.p is None or page <= cli.args.p:
            print(f'Scanning messages in {folder.title()}, page {page:,}')
            html = http_request(f'https://www.furaffinity.net/msg/pms/{page}/', headers, html=True)
            ids = [int(id_) for id_ in RE_MODERN_ID.findall(html) or RE_CLASSIC_ID.findall(html)]

            if not ids:
                break

            unread_messages.extend(int(id_) for id_ in (RE_MODERN_UNREAD.findall(html) or RE_CLASSIC_UNREAD.findall(html)))
            online_index.update((id_, folder) for id_ in ids)
            page += 1

    return online_index


def get_message(id_, folder):
    headers = {'Cookie': f'a={token_a}; b={token_b}; folder={folder}'}
    html = http_request(f'https://www.furaffinity.net/viewmessage/{id_}/', headers, html=True)
    return Message(html=html, id_=id_, folder=folder)


# The folder parameter is probably not necessary, but more research is needed.
# For now, call this function for each folder that contains unread messages,
# and only for messages that were received by the user.
def mark_unread(ids, folder):
    data = [('manage_notes', 1), ('move_to', 'unread')]
    data.extend(('items[]', id_) for id_ in ids)
    headers = {'Cookie': f'a={token_a}; b={token_b}; folder={folder}'}
    http_request('https://www.furaffinity.net/msg/pms/', headers, data)
