import argparse
import os
import sys

from .constants import *


ANSI_SUPPORT = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and os.environ.get('FAPM_ANSI') == '1'


class ArgumentParser(argparse.ArgumentParser):
    def print_help(self):
        print(HELP)

    def error(self, message):
        die(message, 64, True)


def die(message, exit_code=1, show_usage=False):
    if show_usage:
        print(HELP.split('\n\n')[1], end='\n\n')

    print_ansi(f'\033[1m{arg_parser.prog}: \033[31merror: \033[0m{message}')
    sys.exit(exit_code)


def warn(message):
    print_ansi(f'\033[1m{arg_parser.prog}: \033[33mwarning: \033[0m{message}')


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


def print_ansi(*objects, **kwargs):
    if not ANSI_SUPPORT:
        objects = list(objects)

        for i in range(len(objects)):
            if isinstance(objects[i], str):
                objects[i] = RE_ANSI.sub('', objects[i])

    print(*objects, **kwargs)


arg_parser = ArgumentParser(prog='fapm')
arg_parser.add_argument('--version', action='version', version=VERSION)
arg_parser.add_argument('-u', '--update', action='store_true')
arg_parser.add_argument('-a', metavar="UUID", type=uuid_argument)
arg_parser.add_argument('-b', metavar="UUID", type=uuid_argument)
arg_parser.add_argument('-f', metavar="FOLDER", type=folder_argument, nargs='+')
arg_parser.add_argument('-p', metavar="PAGE", type=page_argument)
arg_parser.add_argument('-g', metavar="AGENT")
arg_parser.add_argument('-e', '--no-emojis', action='store_true')
arg_parser.add_argument('-r', '--keep-re', action='store_true')
arg_parser.add_argument('-t', '--sort-by-time', action='store_true')

args = arg_parser.parse_args()
