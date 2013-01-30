from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Binary, DateTime, Column
from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

from aggregator.util import json_dumps, all_


_Model = declarative_base()


class Record(_Model):
    __tablename__ = 'record'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now())
    category = Column(String, nullable=False)
    value = Column(Binary)


record = Record.__table__

PUT_QUERY = """\
insert into record
    (date, category, value)
values
    (:date, :category, :value)
"""


def get_engine(sqluri, pool_size=100, pool_recycle=60, pool_timeout=30):
    extras = {}
    if not sqluri.startswith('sqlite'):
        extras['pool_size'] = pool_size
        extras['pool_timeout'] = pool_timeout
        extras['pool_recycle'] = pool_recycle

    return create_engine(sqluri, **extras)


class Database(object):

    def __init__(self, engine=None, sqluri=None, **params):
        self.engine = engine or get_engine(sqluri, **params)
        record.metadata.bind = self.engine
        record.create(checkfirst=True)
        self.session = self._create_session()

    def _create_session(self):
        return create_session(bind=self.engine)

    def put(self, category="unknown", date=None, **data):
        if date is None:
            date = datetime.now()

        data.setdefault('date', date)

        # store in db
        # XXX try..except etc
        self.engine.execute(PUT_QUERY, date=date, category=category,
                            value=json_dumps(data))

    def put_batch(self, batch):
        session = self._create_session()
        now = datetime.now()
        for item in batch:
            if not isinstance(item, dict):
                item = dict(item)
            date = item.pop('date', now)
            category = item.pop('category', 'unknown')
            session.add(Record(date=date, category=category,
                value=json_dumps(item)))
        session.commit()

    def get(self, category=None, start_date=None, end_date=None):
        if all_((category, start_date, end_date), None):
            raise ValueError("You need to filter something")

        query = self.session.query(Record)

        if category is not None:
            query = query.filter(Record.category == category)

        if start_date is not None:
            query = query.filter(Record.date >= start_date)

        if end_date is not None:
            query = query.filter(Record.date <= end_date)

        return query
