import re
import time

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode
from dateutil import parser as dateutil_parser

from . import cli
from . import db


RE_QUOTE_START = re.compile(r'\[QUOTE\]', re.IGNORECASE)
RE_QUOTE_END = re.compile(r'\[/QUOTE\]', re.IGNORECASE)

RE_MODERN_SUBJECT = re.compile(r'<div class="section-header">.*?<h2>(.*?)</h2>', re.DOTALL)
RE_MODERN_TIMESTAMP = re.compile(r'<div class="section-header">.*?<strong>.+?<span.*?>(.+?)</span>', re.DOTALL)
RE_MODERN_SENDER = re.compile(r'<div class="section-header">.*?<strong>(.+?)</strong>', re.DOTALL)
RE_MODERN_RECEIVER = re.compile(r'<div class="section-header">.*?<strong>.+?<strong>(.+?)</strong>', re.DOTALL)
RE_MODERN_TEXT = re.compile(r'<div class="user-submitted-links">(.*?)</div>', re.DOTALL)
RE_MODERN_USERNAME = re.compile(r'<img class="loggedin_user_avatar .*?<a .*?>(.*?)</a>', re.DOTALL)

RE_CLASSIC_SUBJECT = re.compile(r'<a href="/msg/compose/">.*?<b>(.*?)</b>', re.DOTALL)
RE_CLASSIC_TIMESTAMP = re.compile(r'<a href="/msg/compose/">.*? class="popup_date">(.+?)</span>', re.DOTALL)
RE_CLASSIC_SENDER = re.compile(r'<a href="/msg/compose/">.*?<a .*?<a .*?>(.+?)</a>', re.DOTALL)
RE_CLASSIC_RECEIVER = re.compile(r'<a href="/msg/compose/">.*?<a .*?<a .*?<a .*?>(.+?)</a>', re.DOTALL)
RE_CLASSIC_TEXT = re.compile(r'<a href="/msg/compose/">.*? class="popup_date">.*?<br/><br/>(.+?)</td>', re.DOTALL)
RE_CLASSIC_USERNAME = re.compile(r'<a id="my-username".*?\~(.*?)</a>', re.DOTALL)

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

    def timestamp_format(self, pattern='%Y-%m-%d %H:%M'):
        return time.strftime(pattern, time.localtime(self.timestamp))

    def subject_format(self):
        if cli.args.keep_re:
            return self.subject

        subject = self.subject

        while subject and subject.lower().startswith('re:'):
            subject = subject[3:].lstrip()

        return subject

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
