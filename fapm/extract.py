import re

from dateutil import parser as dateutil_parser

from . import cli


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


def subject(html):
    match = RE_MODERN_SUBJECT.search(html) or RE_CLASSIC_SUBJECT.search(html)
    return match.group(1).strip() or None


def timestamp(html):
    match = RE_MODERN_TIMESTAMP.search(html) or RE_CLASSIC_TIMESTAMP.search(html)

    if match is None:
        cli.die('cannot extract message timestamp')

    return int(dateutil_parser.parse(match.group(1)).timestamp())


def sender(html):
    match = RE_MODERN_SENDER.search(html) or RE_CLASSIC_SENDER.search(html)

    if match is None:
        cli.die('cannot extract message sender')

    return match.group(1).strip()


def receiver(html):
    match = RE_MODERN_RECEIVER.search(html) or RE_CLASSIC_RECEIVER.search(html)

    if match is None:
        cli.die('cannot extract message receiver')

    return match.group(1).strip()


def text(html):
    match = RE_MODERN_TEXT.search(html) or RE_CLASSIC_TEXT.search(html)

    if match is None:
        cli.die('cannot extract message text')

    return match.group(1).replace('\n', '').replace('\r', '').strip()


def username(html):
    match = RE_MODERN_USERNAME.search(html) or RE_CLASSIC_USERNAME.search(html)

    if match is None:
        cli.die('cannot extract username')

    return match.group(1).strip()
