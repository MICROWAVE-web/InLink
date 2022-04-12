from datetime import datetime

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy.exc import DatabaseError
from werkzeug.security import generate_password_hash, check_password_hash

from db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'user'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String(50), unique=True)
    password = sqlalchemy.Column(sqlalchemy.String(500), nullable=False)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)


class Favourites(SqlAlchemyBase):
    __tablename__ = 'favourites'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    url = sqlalchemy.Column(sqlalchemy.String(500))
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("user.id"))
    user = orm.relation('User')
