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


def uuid_argument(value):
    if not RE_UUID.match(value):
        raise argparse.ArgumentTypeError(f'invalid session token: {value}')

    return value


def folder_argument(value):
    if value.lower() == 'outbox':
        warn('Outbox folder is now called Sent')
        value = 'sent'
    elif value.lower() not in FOLDERS:
        raise argparse.ArgumentTypeError(f'invalid folder: {value}')

    return value.lower()


def page_argument(value):
    try:
        value = int(value)

        if value < 1:
            raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(f'invalid page number: {value}')

    return value


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
