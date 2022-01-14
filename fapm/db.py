from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine('sqlite:///messages.db')

Session = sessionmaker(engine)

Model = declarative_base()
Model.metadata.bind = engine
