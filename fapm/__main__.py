import os
import sys

import jinja2
from werkzeug.utils import secure_filename

from . import cli
from . import db
from . import download
from . import query
from .constants import *


def pluralize(count, singular, plural=None):
    return f'{count:,} {singular if count == 1 else plural or singular + "s"}'


db.Model.metadata.create_all()

if cli.args.update:
    download.prompt_session_tokens()
    local_index = query.get_local_index()
    online_index = download.get_online_index()
    new_index = {id_: folder for id_, folder in online_index.items() if id_ not in local_index}
    moved_index = {id_: folder for id_, folder in online_index.items() if id_ in local_index and local_index[id_] != folder}

    if moved_index:
        print(f'Updating {pluralize(len(moved_index), "message")} moved to other folders')

        for id_, folder in moved_index.items():
            query.move_message(id_, folder)

    if new_index:
        unread_index = []
        print(f'Found {pluralize(len(new_index), "message")} not in database')

        with db.Session() as session:
            for id_, folder in new_index.items():
                message = download.get_message(id_, folder)
                print(f'Downloaded message [{message.timestamp_format()}] {message.subject or "No Subject"}')

                if id_ in download.unread_messages and not message.sent:
                    unread_index.append(id_)

                session.add(message)

            session.commit()
            print('Finished downloading messages')

        if unread_index:
            print(f'Marking {pluralize(len(unread_index), "message")} as unread')
            download.mark_messages_unread(unread_index)

    else:
        print('No new messages to download')

jinja_loader = jinja2.FileSystemLoader('templates')
jinja_env = jinja2.Environment(loader=jinja_loader, autoescape=True)
jinja_env.globals.update(secure_filename=secure_filename)
index_template = jinja_env.get_template('index.html')
conversation_template = jinja_env.get_template('conversation.html')

try:
    os.mkdir('html')
except OSError:
    pass

contacts = query.get_contacts()
messages_for_index = []

if not contacts:
    sys.exit('No conversations to format')

print(f'Formatting conversations with {pluralize(len(contacts), "contact")}')

for contact in contacts:
    messages = query.get_conversation(contact)
    messages_for_index.append(messages[-1])

    with open(f'html/{secure_filename(contact)}.html', 'w') as file_:
        file_.write(conversation_template.render(contact=contact, messages=messages))

with open('index.html', 'w') as file_:
    file_.write(index_template.render(messages=messages_for_index))

if cli.args.update:
    print(ABOUT_LOGOUT)
