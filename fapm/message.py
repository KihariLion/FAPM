import re
import time

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode
from dateutil import parser as dateutil_parser

from . import cli
from . import db
from .constants import *


def extract_subject(html):
    match = RE_MODERN_SUBJECT.search(html) or RE_CLASSIC_SUBJECT.search(html)
    return match.group(1).strip() or None


def extract_timestamp(html):
    match = RE_MODERN_TIMESTAMP.search(html) or RE_CLASSIC_TIMESTAMP.search(html)

    if match is None:
        cli.die('cannot extract message timestamp')

    return int(dateutil_parser.parse(match.group(1)).timestamp())


def extract_sender(html):
    match = RE_MODERN_SENDER.search(html) or RE_CLASSIC_SENDER.search(html)

    if match is None:
        cli.die('cannot extract message sender')

    return match.group(1).strip()


def extract_receiver(html):
    match = RE_MODERN_RECEIVER.search(html) or RE_CLASSIC_RECEIVER.search(html)

    if match is None:
        cli.die('cannot extract message receiver')

    return match.group(1).strip()


def extract_text(html):
    match = RE_MODERN_TEXT.search(html) or RE_CLASSIC_TEXT.search(html)

    if match is None:
        cli.die('cannot extract message text')

    return match.group(1).replace('\n', '').replace('\r', '').strip()


def extract_username(html):
    match = RE_MODERN_USERNAME.search(html) or RE_CLASSIC_USERNAME.search(html)

    if match is None:
        cli.die('cannot extract username')

    return match.group(1).strip()


class Message(db.Model):
    __tablename__ = 'message'

    id_ = Column('id', Integer, primary_key=True)
    folder = Column(Unicode, nullable=False)
    sent = Column(Integer, nullable=False)
    subject = Column(Unicode)
    timestamp = Column(Integer, nullable=False)
    sender = Column(Unicode, nullable=False)
    receiver = Column(Unicode, nullable=False)
    text = Column(Unicode, nullable=False)

    def __init__(self, html=None, *pargs, **kwargs):
        if html:
            kwargs['subject'] = extract_subject(html)
            kwargs['timestamp'] = extract_timestamp(html)
            kwargs['sender'] = extract_sender(html)
            kwargs['receiver'] = extract_receiver(html)
            kwargs['text'] = extract_text(html)
            kwargs['sent'] = 1 if extract_username(html) == kwargs['sender'] else 0

        super().__init__(*pargs, **kwargs)

    @property
    def contact(self):
        return self.receiver if self.sent else self.sender

    def subject_format(self):
        if cli.args.keep_re:
            return self.subject

        subject = self.subject

        while subject and subject.lower().startswith('re:'):
            subject = subject[3:].lstrip()

        return subject

    def timestamp_format(self, pattern='%Y-%m-%d %H:%M'):
        return time.strftime(pattern, time.localtime(self.timestamp))

    def text_format(self):
        text = self.text

        # FurAffinity's BBCode parser still cannot handle nested quotes.
        # Replacing the BBCode tags with the appropriate HTML works, but might
        # not be valid in all situations. More research is needed.
        text = RE_QUOTE_START.sub('<span class="bbcode bbcode_quote">', text)
        text = RE_QUOTE_END.sub('</span>', text)

        for smilie in SMILIE_REPLACEMENTS:
            text = text.replace(smilie[0], smilie[1 if cli.args.no_emojis else 2])

        return text
