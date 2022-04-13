from flask import jsonify
from flask_restful import reqparse, abort, Resource

from parsers.reqparse_favourite import fav_parser
from parsers.reqparse_user import user_parser
from views import app
import db_session
from models import User, Favourites


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def abort_if_fav_not_found(fav_id):
    session = db_session.create_session()
    user = session.query(Favourites).get(fav_id)
    if not user:
        abort(404, message=f"Favourite {fav_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        news = session.query(User).get(user_id)
        return jsonify({'user': news.to_dict(
            only=('id', 'email', 'date'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('email', 'password', 'date')) for item in news]})

    def post(self):
        args = user_parser.parse_args()
        session = db_session.create_session()
        user = User(
            email=args['email'],
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self):
        args = user_parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).filter_by(id=args['id'])
        user.email = args['email']
        user.set_password(args['password'])
        session.commit()
        return jsonify({'success': 'OK'})


class FavouriteResource(Resource):
    def get(self, fav_id):
        abort_if_fav_not_found(fav_id)
        session = db_session.create_session()
        fav = session.query(Favourites).get(fav_id)
        return jsonify({'user': fav.to_dict(
            only=('id', 'url', 'date', 'user_id'))})

    def delete(self, fav_id):
        abort_if_fav_not_found(fav_id)
        session = db_session.create_session()
        fav = session.query(User).get(fav_id)
        session.delete(fav)
        session.commit()
        return jsonify({'success': 'OK'})


class FavouriteListResource(Resource):
    def get(self):
        session = db_session.create_session()
        fav = session.query(Favourites).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'url', 'date', 'user_id')) for item in fav]})

    def post(self):
        args = fav_parser.parse_args()
        session = db_session.create_session()
        fav = Favourites(
            url=args['url'],
            user_id=args['user_id']
        )
        fav.user = session.query(User).filter_by(id=args['user_id'])
        session.add(fav)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self):
        args = fav_parser.parse_args()
        session = db_session.create_session()
        fav = session.query(Favourites).filter_by(id=args['id'])
        fav.email = args['url']
        fav.email = args['user_id']
        fav.user = session.query(User).filter_by(id=args['user_id'])
        session.commit()
        return jsonify({'success': 'OK'})
