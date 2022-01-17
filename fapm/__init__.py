__author__ = 'Kihari'
__license__ = 'BSD'
__version__ = '2022.1.16.0'


import re


FOLDERS = ('inbox', 'outbox', 'archive', 'trash')

RE_SESSION_TOKEN = re.compile('^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$')


def is_folder(value):
    return value in FOLDERS


def is_session_token(value):
    return isinstance(value, str) and RE_SESSION_TOKEN.match(value) is not None
