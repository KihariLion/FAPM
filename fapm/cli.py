import argparse
import sys

from . import __version__ as VERSION, is_folder, is_session_token


HELP = f"""
FurAffinity Private Message Downloader
Version {VERSION}
https://www.github.com/kiharilion

Usage: python3 -m fapm --help
       python3 -m fapm --version
       python3 -m fapm [-u] [-a UUID] [-b UUID] [-f FOLDER...] [-e] [-r]

Downloads private messages from FurAffinity, splits them into conversations
with individual users, and generates an HTML document for each conversation
that can be viewed in a web browser.

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

USAGE = HELP.split('\n\n')[1]


class ArgumentParser(argparse.ArgumentParser):
    def print_help(self):
        print(HELP)

    def error(self, message):
        die(message, 64, True)


def die(message, exit_code=1, show_usage=False):
    if show_usage:
        print(USAGE, end='\n\n')

    print(f'\033[1m{arg_parser.prog}: \033[31merror: \033[0m{message}')
    sys.exit(exit_code)


def prompt_session_token(name):
    value = input(f'UUID for session token {name}: ').strip()
    return value if is_session_token(value) else None


def valid_folder_type(value):
    if not is_folder(value.lower()):
        raise argparse.ArgumentTypeError(f'invalid folder name: {value}')

    return value.lower()


def valid_session_token_type(value):
    if not is_session_token(value):
        raise argparse.ArgumentTypeError(f'invalid session token: {value}')

    return value


arg_parser = ArgumentParser(prog='fapm')
arg_parser.add_argument('--version', action='version', version=VERSION)
arg_parser.add_argument('-u', '--update', action='store_true')
arg_parser.add_argument('-a', type=valid_session_token_type)
arg_parser.add_argument('-b', type=valid_session_token_type)
arg_parser.add_argument('-f', nargs='+', type=valid_folder_type)
arg_parser.add_argument('-e', '--no-emojis', action='store_true')
arg_parser.add_argument('-r', '--keep-re', action='store_true')

args = arg_parser.parse_args()
