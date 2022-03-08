from sqlalchemy.sql.expression import label, or_

from . import db
from .message import Message


def get_database_index():
    with db.Session() as session:
        messages = session.query(Message.id_, Message.folder) \
          .order_by(Message.id_.desc()) \
          .all()

    return {key:value for key, value in messages}


def move_message(id_, folder):
    with db.Session() as session:
        message = session.query(Message).get(id_)
        message.folder = folder
        session.add(message)
        session.commit()


def get_contacts():
    with db.Session() as session:
        senders = session \
          .query(label('username', Message.sender)) \
          .filter_by(sent=0)

        receivers = session \
          .query(label('username', Message.receiver)) \
          .filter_by(sent=1)

    usernames = senders.union(receivers).distinct()
    key = lambda username: username.lower()
    return sorted((username for username, in usernames), key=key)


def get_conversation(username):
    with db.Session() as session:
        return session.query(Message) \
          .filter(or_(Message.sender == username, Message.receiver == username)) \
          .order_by(Message.id_) \
          .all()
