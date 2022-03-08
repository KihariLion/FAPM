import argparse
import sys

from .constants import *


class ArgumentParser(argparse.ArgumentParser):
    def print_help(self):
        print(HELP)

    def error(self, message):
        die(message, 64, True)


def die(message, exit_code=1, show_usage=False):
    if show_usage:
        print(HELP.split('\n\n')[1], end='\n\n')

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


def is_folder(value):
    return value in FOLDERS


def is_session_token(value):
    return isinstance(value, str) and RE_UUID.match(value) is not None


arg_parser = ArgumentParser(prog='fapm')
arg_parser.add_argument('--version', action='version', version=VERSION)
arg_parser.add_argument('-u', '--update', action='store_true')
arg_parser.add_argument('-a', type=valid_session_token_type)
arg_parser.add_argument('-b', type=valid_session_token_type)
arg_parser.add_argument('-f', nargs='+', type=valid_folder_type)
arg_parser.add_argument('-e', '--no-emojis', action='store_true')
arg_parser.add_argument('-r', '--keep-re', action='store_true')

args = arg_parser.parse_args()
