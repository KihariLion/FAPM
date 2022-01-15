import re
import time

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Unicode

from . import cli
from . import db
from . import extract


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
            kwargs['subject'] = extract.subject(html)
            kwargs['timestamp'] = extract.timestamp(html)
            kwargs['sender'] = extract.sender(html)
            kwargs['receiver'] = extract.receiver(html)
            kwargs['text'] = extract.text(html)
            kwargs['sent'] = 1 if extract.username(html) == kwargs['sender'] else 0

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
