import os
import re
import sys
import time
import urllib.request
from argparse import ArgumentParser as ArgumentParser_

import jinja2
from dateutil import parser as dateutil_parser
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.sql.expression import label, or_


VERSION = '2021.10.6.0'

USAGE = """
Usage: python3 fapm.py --help
       python3 fapm.py [-u] [-a UUID] [-b UUID] [-e]
""".strip()

HELP = f"""
FurAffinity Private Message Downloader
Version {VERSION}
https://www.github.com/kiharilion

{USAGE}

Downloads private messages from FurAffinity, splits them into conversations
with individual users, and generates an HTML document for each conversation
that can be viewed in a web browser.

Note that this script will mark all messages sent to you as having been read,
even if you have not viewed them on FurAffinity itself.

Optional Arguments:
  -h, --help       Show this help message and exit.
  -u, --update     Check for new private messages and download them.
  -a UUID          Specify session token A instead of prompting for it.
  -b UUID          Specify session token B instead of prompting for it.
  -e, --no-emojis  Replace smilies with BBCode text instead of emojis.
""".strip()

ABOUT_SESSION_COOKIES = """
In Firefox, sign into your FurAffinity account, then press SHIFT F9 to open the
Storage Inspector window. The cookies named A and B have values that might look
similar to this:

  abcdef01-2345-6789-abcd-ef0123456789

Double-click on a value to highlight it, then press CTRL C to copy it. Paste
each of the values into the prompt below.
""".lstrip()

ABOUT_FIRST_UPDATE = f"""
{USAGE}

You have not downloaded any messages yet! Rerun the script with the --update
option enabled. See --help for more information.
""".strip()

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
RE_MODERN_SUBJECT = re.compile(r'<div class="section-header">.*?<h2>(.*?)</h2>', re.DOTALL)
RE_MODERN_TIMESTAMP = re.compile(r'<div class="section-header">.*?<strong>.+?<span.*?>(.+?)</span>', re.DOTALL)
RE_MODERN_SENDER = re.compile(r'<div class="section-header">.*?<strong>(.+?)</strong>', re.DOTALL)
RE_MODERN_RECEIVER = re.compile(r'<div class="section-header">.*?<strong>.+?<strong>(.+?)</strong>', re.DOTALL)
RE_MODERN_TEXT = re.compile(r'<div class="user-submitted-links">(.*?)</div>', re.DOTALL)
RE_MODERN_USERNAME = re.compile(r'<img class="loggedin_user_avatar .*?<a .*?>(.*?)</a>', re.DOTALL)

RE_CLASSIC_ID = re.compile(r'href="/viewmessage/(\d+)/"')
RE_CLASSIC_SUBJECT = re.compile(r'<a href="/msg/compose/">.*?<b>(.*?)</b>', re.DOTALL)
RE_CLASSIC_TIMESTAMP = re.compile(r'<a href="/msg/compose/">.*? class="popup_date">(.+?)</span>', re.DOTALL)
RE_CLASSIC_SENDER = re.compile(r'<a href="/msg/compose/">.*?<a .*?<a .*?>(.+?)</a>', re.DOTALL)
RE_CLASSIC_RECEIVER = re.compile(r'<a href="/msg/compose/">.*?<a .*?<a .*?<a .*?>(.+?)</a>', re.DOTALL)
RE_CLASSIC_TEXT = re.compile(r'<a href="/msg/compose/">.*? class="popup_date">.*?<br/><br/>(.+?)</td>', re.DOTALL)
RE_CLASSIC_USERNAME = re.compile(r'<a id="my-username".*?\~(.*?)</a>', re.DOTALL)

RE_UUID = re.compile('^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')

RE_QUOTE_START = re.compile(r'\[QUOTE\]', re.IGNORECASE)
RE_QUOTE_END = re.compile(r'\[/QUOTE\]', re.IGNORECASE)

SMILIE_REPLACEMENTS = (
  ('<i class="smilie tongue"></i>', ':-p', '&#128539;'),
  ('<i class="smilie cool"></i>', ':cool:', '&#128526;'),
  ('<i class="smilie wink"></i>', ';-)', '&#128521;'),
  ('<i class="smilie oooh"></i>', ':-o', '&#128558;'),
  ('<i class="smilie smile"></i>', ':-)', '&#128578;'),
  ('<i class="smilie evil"></i>', ':evil:', '&#128520;'),
  ('<i class="smilie huh"></i>', ':huh:', '&#128533;'),
  ('<i class="smilie whatever"></i>', ':whatever:', '&#128535;'),
  ('<i class="smilie angel"></i>', ':angel:', '&#128519;'),
  ('<i class="smilie badhairday"></i>', ':badhair:', '&#128534;'),
  ('<i class="smilie lmao"></i>', ':lmao:', '&#128518;'),
  ('<i class="smilie cd"></i>', ':cd:', '&#128191;'),
  ('<i class="smilie crying"></i>', ':cry:', '&#128549;'),
  ('<i class="smilie dunno"></i>', ':idunno:', '&#128528;'),
  ('<i class="smilie embarrassed"></i>', ':embarrassed:', '&#128522;'),
  ('<i class="smilie gift"></i>', ':gift:', '&#127873;'),
  ('<i class="smilie coffee"></i>', ':coffee:', '&#127866;&#65039;'),
  ('<i class="smilie love"></i>', ':love:', '&#10084;&#65039;'),
  ('<i class="smilie nerd"></i>', ':isanerd:', '&#129299;'),
  ('<i class="smilie note"></i>', ':note:', '&#127925;'),
  ('<i class="smilie derp"></i>', ':derp:', '&#129396;'),
  ('<i class="smilie sarcastic"></i>', ':sarcastic:', '&#129320;'),
  ('<i class="smilie serious"></i>', ':serious:', '&#128528;'),
  ('<i class="smilie sad"></i>', ':-(', '&#128577;'),
  ('<i class="smilie sleepy"></i>', ':sleepy:', '&#128564;'),
  ('<i class="smilie teeth"></i>', ':teeth:', '&#128544;'),
  ('<i class="smilie veryhappy"></i>', ':veryhappy:', '&#128515;'),
  ('<i class="smilie yelling"></i>', ':yelling:', '&#129324;'),
  ('<i class="smilie zipped"></i>', ':zipped:', '&#129296;'))


# Change ArgumentParser's output formatting.
class ArgumentParser(ArgumentParser_):
    def print_help(self):
        print(HELP)

    def error(self, message):
        print(f'{USAGE}\n\n{self.prog}: error: {message}')
        sys.exit(64)


Model = declarative_base()


class Message(Model):
    __tablename__ = 'message'

    id_ = Column('id', Integer, primary_key=True)
    folder = Column(Unicode, nullable=False)
    sent = Column(Integer, nullable=False)
    subject = Column(Unicode)
    timestamp = Column(Integer, nullable=False)
    sender = Column(Unicode, nullable=False)
    receiver = Column(Unicode, nullable=False)
    text = Column(Unicode, nullable=False)

    def __init__(self, html=None, *args, **kwargs):
        if html:
            kwargs['subject'] = extract_subject(html)
            kwargs['timestamp'] = extract_timestamp(html)
            kwargs['sender'] = extract_sender(html)
            kwargs['receiver'] = extract_receiver(html)
            kwargs['text'] = extract_text(html)
            kwargs['sent'] = 1 if extract_username(html) == kwargs['sender'] else 0

        super().__init__(*args, **kwargs)

    @property
    def contact(self):
        return self.receiver if self.sent else self.sender

    @classmethod
    def newest_in_folder(cls, folder):
        return db_session.query(cls) \
          .filter_by(folder=folder) \
          .order_by(cls.id_.desc()) \
          .first()

    @classmethod
    def conversation_with(cls, username):
        return db_session.query(cls) \
          .filter(or_(cls.sender == username, cls.receiver == username)) \
          .order_by(cls.id_) \
          .all()

    def timestamp_format(self, pattern='%Y-%m-%d %-I:%M%P'):
        return time.strftime(pattern, time.localtime(self.timestamp))

    def text_format(self):
        text = self.text

        # FurAffinity's BBCode parser still cannot handle nested quotes.
        # Replacing the BBCode tags with the appropriate HTML works, but might
        # not be valid in all situations. More research is needed.
        text = RE_QUOTE_START.sub('<span class="bbcode bbcode_quote">', text)
        text = RE_QUOTE_END.sub('</span>', text)

        for smilie in SMILIE_REPLACEMENTS:
            text = text.replace(smilie[0], smilie[1 if args.no_emojis else 2])

        return text


def _extract(html, re_modern, re_classic, required_name=False):
    match = re_modern.search(html) or re_classic.search(html)

    if required_name and not match:
        raise RuntimeError(f'Cannot extract {required_name} from HTML')

    return match.group(1).strip()


def extract_subject(html):
    return _extract(html, RE_MODERN_SUBJECT, RE_CLASSIC_SUBJECT) or None


def extract_timestamp(html):
    match = _extract(html, RE_MODERN_TIMESTAMP, RE_CLASSIC_TIMESTAMP, 'timestamp')
    return int(dateutil_parser.parse(match).timestamp())


def extract_sender(html):
    return _extract(html, RE_MODERN_SENDER, RE_CLASSIC_SENDER, 'sender')


def extract_receiver(html):
    return _extract(html, RE_MODERN_RECEIVER, RE_CLASSIC_RECEIVER, 'receiver')


def extract_text(html):
    match = _extract(html, RE_MODERN_TEXT, RE_CLASSIC_TEXT, 'text')
    return match.replace('\n', '').replace('\r', '').strip()


def extract_username(html):
    return _extract(html, RE_MODERN_USERNAME, RE_CLASSIC_USERNAME, 'username')


def query_own_username():
    sender = db_session.query(Message.sender) \
      .filter_by(sent=1) \
      .limit(1) \
      .scalar()

    if sender is None:
        receiver = db_session.query(Message.receiver) \
          .filter_by(sent=0) \
          .limit(1) \
          .scalar()

    # If the database contains no messages, this will return None.
    return sender or receiver


def query_contacts(own_username=None):
    if own_username is None:
        own_username = query_own_username()

    senders = db_session \
      .query(label('username', Message.sender)) \
      .filter(Message.sender != own_username)

    receivers = db_session \
      .query(label('username', Message.receiver)) \
      .filter(Message.receiver != own_username)

    usernames = senders.union(receivers).distinct()
    key = lambda username: username.lower()
    return sorted((username for username, in usernames), key=key)


def prompt_session_token(name):
    token = input(f'UUID for session token {name}: ').strip()

    # Checking that the token is a valid UUID helps ensure that the user
    # entered the correct value.
    return token if RE_UUID.match(token) else None


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


if __name__ == '__main__':
    arg_parser = ArgumentParser(prog='fapm')
    arg_parser.add_argument('-u', '--update', action='store_true')
    arg_parser.add_argument('-a')
    arg_parser.add_argument('-b')
    arg_parser.add_argument('-e', '--no-emojis', action='store_true')
    args = arg_parser.parse_args()

    db_engine = create_engine('sqlite:///messages.db')
    Model.metadata.bind = db_engine
    Model.metadata.create_all()
    db_sessionmaker = sessionmaker(db_engine)
    db_session = scoped_session(db_sessionmaker)

    if args.update:
        uuid_a = args.a if args.a and RE_UUID.match(args.a) else None
        uuid_b = args.b if args.b and RE_UUID.match(args.b) else None
        need_session_tokens = uuid_a is None or uuid_b is None

        if need_session_tokens:
            print(ABOUT_SESSION_COOKIES)

        while uuid_a is None:
            uuid_a = prompt_session_token('A')

        while uuid_b is None:
            uuid_b = prompt_session_token('B')

        if need_session_tokens:
            print()

        new_message_count = 0

        for folder in ('inbox', 'outbox', 'archive', 'trash'):
            page = 1
            ids = download_ids(folder, page, uuid_a, uuid_b)
            newest_message = Message.newest_in_folder(folder)

            while ids:
                for id_ in ids:
                    if newest_message and id_ <= newest_message.id_:
                        ids = None
                        break

                    message = download_message(id_, folder, uuid_a, uuid_b)
                    print(f'{message.timestamp_format("%Y-%m-%d %H:%M")} [{folder.title()}] {message.subject}')
                    db_session.add(message)
                    new_message_count += 1
                    time.sleep(SLEEP)

                if ids:
                    page += 1
                    ids = download_ids(folder, page, uuid_a, uuid_b)

        print(f'{new_message_count:,} new message{"" if new_message_count == 1 else "s"} downloaded')
        db_session.commit()

    jinja2_loader = jinja2.FileSystemLoader('templates')
    jinja2_env = jinja2.Environment(loader=jinja2_loader, autoescape=True)
    index_template = jinja2_env.get_template('index.html')
    conversation_template = jinja2_env.get_template('conversation.html')

    try:
        os.mkdir('html')
    except OSError:
        pass

    contacts = query_contacts()
    messages_for_index = []

    if not args.update and not contacts:
        sys.exit(ABOUT_FIRST_UPDATE)

    print(f'Formatting conversations with {len(contacts):,} contacts')

    for contact in contacts:
        messages = Message.conversation_with(contact)
        messages_for_index.append(messages[-1])

        with open(f'html/{contact}.html', 'w') as file_:
            file_.write(conversation_template.render(contact=contact, messages=messages))

    with open('index.html', 'w') as file_:
        file_.write(index_template.render(messages=messages_for_index))

    db_session.close()

    if args.update:
        print(ABOUT_LOG_OUT)
