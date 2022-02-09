from datetime import datetime

import sqlalchemy
from sqlalchemy.exc import DatabaseError

from views import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"


def initializing():
    db.create_all()


if __name__ == '__main__':
    initializing()
