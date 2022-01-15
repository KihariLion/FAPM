import re
import time
import urllib.request

from . import __version__ as VERSION, FOLDERS, is_session_token
from . import cli
from .message import Message


ABOUT_COOKIES = """
In Firefox, sign into your FurAffinity account, then press SHIFT F9 to open the
Storage Inspector window. The cookies named A and B have values that might look
similar to this:

  abcdef01-2345-6789-abcd-ef0123456789

Double-click on a value to highlight it, then press CTRL C to copy it. Paste
each of the values into the prompt below.

WARNING!

When you enter your session cookie data, you will give this program complete
control over your FurAffinity account. Only you can decide whether or not you
trust this software and wish to continue using it.
""".lstrip()

RE_MODERN_ID = re.compile(r'/msg/pms/\d+/(\d+)/#message')
RE_CLASSIC_ID = re.compile(r'href="/viewmessage/(\d+)/"')

# The number of seconds to pause after each HTTP request. Do not change this
# value to a smaller number! Clobbering FurAffinity's servers hurts us all.
# Be considerate to your fellow furries and be patient. You can let the script
# run overnight if you have a lot of messages to download.
SLEEP = 5


token_a = cli.args.a if cli.args.a and is_session_token(cli.args.a) else None
token_b = cli.args.b if cli.args.b and is_session_token(cli.args.b) else None
folders = tuple(set(cli.args.f)) if cli.args.f else FOLDERS


def _get_ids(folder, page):
    print(f'Enumerating messages in {folder.title()}, page {page:,}')
    request = urllib.request.Request(f'https://www.furaffinity.net/msg/pms/{page}/')
    request.add_header('Cookie', f'a={token_a}; b={token_b}; folder={folder}')
    request.add_header('Host', 'www.furaffinity.net')
    request.add_header('User-Agent', f'FAPM/{VERSION}')
    html = urllib.request.urlopen(request).read().decode()
    time.sleep(SLEEP)
    ids = RE_MODERN_ID.findall(html) or RE_CLASSIC_ID.findall(html)
    return [int(id_) for id_ in ids]


def prompt_session_tokens():
    global token_a
    global token_b

    if token_a is None or token_b is None:
        print(ABOUT_COOKIES)

        while not is_session_token(token_a):
            token_a = input(f'UUID for session token A: ').strip()

        while not is_session_token(token_b):
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
