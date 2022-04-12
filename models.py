from datetime import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy.exc import DatabaseError
from werkzeug.security import generate_password_hash, check_password_hash

from views import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)


def initializing():
    db.create_all()


if __name__ == '__main__':
    initializing()
