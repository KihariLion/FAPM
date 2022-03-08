import re as _re

from . import __version__


HELP = """
FurAffinity Private Message Downloader
https://www.github.com/kiharilion

Usage: python3 -m fapm --help
       python3 -m fapm --version
       python3 -m fapm [-u] [-a UUID] [-b UUID] [-f FOLDER...] [-e] [-r]

Download private messages from FurAffinity, split them into conversations with
individual users, and generate an HTML document for each conversation that can
be viewed in a web browser.

Optional Arguments:
  -h, --help       Show this help message and exit.
  --version        Show version number and exit.
  -u, --update     Check for new private messages and download them.
  -a UUID          Specify session token A instead of prompting for it.
  -b UUID          Specify session token B instead of prompting for it.
  -f FOLDER...     Check for new messages only in the specified folders.
  -e, --no-emojis  Replace smilies with BBCode text.
  -r, --keep-re    Do not strip RE: from message subjects.
""".strip()

VERSION = __version__

ABOUT_COOKIES = """
In Firefox, sign into your FurAffinity account, then press SHIFT F9 to open the
Storage Inspector window. The cookies named A and B have values that might look
similar to this:

  abcdef01-2345-6789-abcd-ef0123456789

Double-click on a value to highlight it, then press CTRL C to copy it. Paste
each of the values into the prompt below.

WARNING: By entering your session data, you are giving this program complete
control over your FurAffinity account. Only you can decide whether or not you
trust this software and wish to continue using it.
""".lstrip()

ABOUT_LOGOUT = """
For your security, you should log out of your FurAffinity account. This will
invalidate the session cookies you provided to this script.
""".rstrip()

RE_UUID = _re.compile('^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$')
RE_QUOTE_START = _re.compile(r'\[QUOTE\]', _re.IGNORECASE)
RE_QUOTE_END = _re.compile(r'\[/QUOTE\]', _re.IGNORECASE)

RE_MODERN_ID = _re.compile(r'/msg/pms/\d+/(\d+)/#message')
RE_MODERN_UNREAD = _re.compile(r'<a class=".*?note-unread.*?" href="/msg/pms/\d+/(\d+)/#message')
RE_MODERN_SUBJECT = _re.compile(r'<div class="section-header">.*?<h2>(.*?)</h2>', _re.DOTALL)
RE_MODERN_TIMESTAMP = _re.compile(r'<div class="section-header">.*?<strong>.+?<span.*?>(.+?)</span>', _re.DOTALL)
RE_MODERN_SENDER = _re.compile(r'<div class="section-header">.*?<strong>(.+?)</strong>', _re.DOTALL)
RE_MODERN_RECEIVER = _re.compile(r'<div class="section-header">.*?<strong>.+?<strong>(.+?)</strong>', _re.DOTALL)
RE_MODERN_TEXT = _re.compile(r'<div class="user-submitted-links">(.*?)</div>', _re.DOTALL)
RE_MODERN_USERNAME = _re.compile(r'<img class="loggedin_user_avatar .*?<a .*?>(.*?)</a>', _re.DOTALL)

RE_CLASSIC_ID = _re.compile(r'href="/viewmessage/(\d+)/"')
RE_CLASSIC_UNREAD = _re.compile(r'<a class=".*?note-unread.*?" href="/viewmessage/(\d+)/"')
RE_CLASSIC_SUBJECT = _re.compile(r'<a href="/msg/compose/">.*?<b>(.*?)</b>', _re.DOTALL)
RE_CLASSIC_TIMESTAMP = _re.compile(r'<a href="/msg/compose/">.*? class="popup_date">(.+?)</span>', _re.DOTALL)
RE_CLASSIC_SENDER = _re.compile(r'<a href="/msg/compose/">.*?<a .*?<a .*?>(.+?)</a>', _re.DOTALL)
RE_CLASSIC_RECEIVER = _re.compile(r'<a href="/msg/compose/">.*?<a .*?<a .*?<a .*?>(.+?)</a>', _re.DOTALL)
RE_CLASSIC_TEXT = _re.compile(r'<a href="/msg/compose/">.*? class="popup_date">.*?<br/><br/>(.+?)</td>', _re.DOTALL)
RE_CLASSIC_USERNAME = _re.compile(r'<a id="my-username".*?\~(.*?)</a>', _re.DOTALL)

# The number of seconds to pause after each HTTP request. Do not change this
# value to a smaller number! Clobbering FurAffinity's servers hurts us all.
# Be considerate to your fellow furries and be patient. You can let the script
# run overnight if you have a lot of messages to download.
HTTP_SLEEP = 5

# The number of times to attempt an HTTP request before giving up.
HTTP_ATTEMPTS = 3

FOLDERS = ('inbox', 'outbox', 'archive', 'trash')

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
