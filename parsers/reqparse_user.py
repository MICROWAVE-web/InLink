from flask_restful import reqparse

user_parser = reqparse.RequestParser()
user_parser.add_argument('id', required=False)
user_parser.add_argument('email', required=True)
user_parser.add_argument('password', required=True)
