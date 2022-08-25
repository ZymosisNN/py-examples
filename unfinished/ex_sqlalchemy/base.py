from contextlib import contextmanager

import sqlalchemy as sa
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pathlib import Path


DATABASE = {
    'drivername': 'sqlite',
    # 'host': 'localhost',
    # 'port': '5432',
    # 'username': 'admin',
    # 'password': 'adminpass',
    'database': str(Path(__file__).parent / 'test.db'),
}


engine = sa.create_engine(URL.create(**DATABASE), echo=True)
Session = sessionmaker(bind=engine)


@contextmanager
def session(**kwargs):
    new_session = Session(**kwargs)
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


Base = declarative_base()


def create_db():
    Base.metadata.create_all(engine)
