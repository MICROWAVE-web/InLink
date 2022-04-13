from flask_restful import reqparse

fav_parser = reqparse.RequestParser()
fav_parser.add_argument('id', required=False)
fav_parser.add_argument('url', required=True)
fav_parser.add_argument('user_id', required=True)
