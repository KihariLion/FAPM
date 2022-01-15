import os
import re
import sys
import time
import urllib.request

import jinja2
from sqlalchemy.sql.expression import label, or_
from werkzeug.utils import secure_filename

from . import __version__ as VERSION, FOLDERS, is_folder, is_session_token
from . import cli
from . import db
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

ABOUT_LOG_OUT = """
For your security, you should log out of your FurAffinity account. This will
invalidate the session cookies you provided to this script.
""".rstrip()

# The number of seconds to pause after downloading a message. Do not change
# this to a smaller number! Clobbering FurAffinity's servers hurts us all.
# Be considerate to your fellow furries and be patient. You can let the script
# run overnight if you have a lot of messages to download.
SLEEP = 5

RE_MODERN_ID = re.compile(r'/msg/pms/\d+/(\d+)/#message')
RE_CLASSIC_ID = re.compile(r'href="/viewmessage/(\d+)/"')


def query_newest_id(folder):
    return session.query(Message.id_) \
      .filter_by(folder=folder) \
      .order_by(Message.id_.desc()) \
      .limit(1) \
      .scalar()


def query_conversation(username):
    return session.query(Message) \
      .filter(or_(Message.sender == username, Message.receiver == username)) \
      .order_by(Message.id_) \
      .all()


def query_contacts():
    senders = session \
      .query(label('username', Message.sender)) \
      .filter_by(sent=0)

    receivers = session \
      .query(label('username', Message.receiver)) \
      .filter_by(sent=1)

    usernames = senders.union(receivers).distinct()
    key = lambda username: username.lower()
    return sorted((username for username, in usernames), key=key)


def download_ids(folder, page, uuid_a, uuid_b):
    request = urllib.request.Request(f'https://www.furaffinity.net/msg/pms/{page}/')
    request.add_header('Cookie', f'a={uuid_a}; b={uuid_b}; folder={folder}')
    request.add_header('Host', 'www.furaffinity.net')
    request.add_header('User-Agent', f'FAPM/{VERSION}')
    html = urllib.request.urlopen(request).read().decode()
    ids = RE_MODERN_ID.findall(html) or RE_CLASSIC_ID.findall(html)
    return tuple(int(id_) for id_ in ids)


def download_message(id_, folder, uuid_a, uuid_b):
    request = urllib.request.Request(f'https://www.furaffinity.net/viewmessage/{id_}/')
    request.add_header('Cookie', f'a={uuid_a}; b={uuid_b}; folder={folder}')
    request.add_header('Host', 'www.furaffinity.net')
    request.add_header('User-Agent', f'FAPM/{VERSION}')
    html = urllib.request.urlopen(request).read().decode()
    return Message(html=html, id_=id_, folder=folder)


db.Model.metadata.create_all()

with db.Session() as session:
    if cli.args.update:
        uuid_a = cli.args.a if cli.args.a and is_session_token(cli.args.a) else None
        uuid_b = cli.args.b if cli.args.b and is_session_token(cli.args.b) else None
        need_session_tokens = uuid_a is None or uuid_b is None

        if need_session_tokens:
            print(ABOUT_COOKIES)

        while uuid_a is None:
            uuid_a = cli.prompt_session_token('A')

        while uuid_b is None:
            uuid_b = cli.prompt_session_token('B')

        if need_session_tokens:
            print()

        folders = tuple(set(cli.args.f)) if cli.args.f else FOLDERS
        new_message_count = 0

        for folder in folders:
            page = 1
            ids = download_ids(folder, page, uuid_a, uuid_b)
            newest_id = query_newest_id(folder)

            while ids:
                for id_ in ids:
                    if newest_id and id_ <= newest_id:
                        ids = None
                        break

                    message = download_message(id_, folder, uuid_a, uuid_b)
                    print(f'{message.timestamp_format()} [{folder.title()}] {message.subject}')
                    session.add(message)
                    new_message_count += 1
                    time.sleep(SLEEP)

                if ids:
                    page += 1
                    ids = download_ids(folder, page, uuid_a, uuid_b)

        print(f'{new_message_count:,} new message{"" if new_message_count == 1 else "s"} downloaded')
        session.commit()

    jinja_loader = jinja2.FileSystemLoader('templates')
    jinja_env = jinja2.Environment(loader=jinja_loader, autoescape=True)
    jinja_env.globals.update(secure_filename=secure_filename)
    index_template = jinja_env.get_template('index.html')
    conversation_template = jinja_env.get_template('conversation.html')

    try:
        os.mkdir('html')
    except OSError:
        pass

    contacts = query_contacts()
    messages_for_index = []

    if not contacts:
        sys.exit('No conversations to format')

    print(f'Formatting conversations with {len(contacts):,} contacts')

    for contact in contacts:
        messages = query_conversation(contact)
        messages_for_index.append(messages[-1])

        with open(f'html/{secure_filename(contact)}.html', 'w') as file_:
            file_.write(conversation_template.render(contact=contact, messages=messages))

    with open('index.html', 'w') as file_:
        file_.write(index_template.render(messages=messages_for_index))

    if cli.args.update:
        print(ABOUT_LOG_OUT)
