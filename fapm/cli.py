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

    print(f'{arg_parser.prog}: error: {message}')
    sys.exit(exit_code)


def warn(message):
    print(f'{arg_parser.prog}: warning: {message}')


def prompt_session_token(name):
    value = input(f'UUID for session token {name}: ').strip()
    return value if is_uuid(value) else None


def folder_argument(value):
    if not is_folder(value.lower()):
        raise argparse.ArgumentTypeError(f'invalid folder: {value}')

    return value.lower()


def uuid_argument(value):
    if not is_uuid(value):
        raise argparse.ArgumentTypeError(f'invalid session token: {value}')

    return value


def page_argument(value):
    try:
        value = int(value)

        if value < 1:
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(f'invalid page number: {value}')

    return value


def is_folder(value):
    return value in FOLDERS


def is_uuid(value):
    return isinstance(value, str) and RE_UUID.match(value) is not None


arg_parser = ArgumentParser(prog='fapm')
arg_parser.add_argument('--version', action='version', version=VERSION)
arg_parser.add_argument('-u', '--update', action='store_true')
arg_parser.add_argument('-a', metavar="UUID", type=uuid_argument)
arg_parser.add_argument('-b', metavar="UUID", type=uuid_argument)
arg_parser.add_argument('-f', metavar="FOLDER", type=folder_argument, nargs='+')
arg_parser.add_argument('-p', metavar="PAGE", type=page_argument)
arg_parser.add_argument('-e', '--no-emojis', action='store_true')
arg_parser.add_argument('-r', '--keep-re', action='store_true')

args = arg_parser.parse_args()
