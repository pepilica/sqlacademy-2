from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from data.users import User, generate_password_hash
from data import db_session


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('surname', required=True)
parser.add_argument('position', required=True)
parser.add_argument('speciality', required=True)
parser.add_argument('address', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password', required=True)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('age', required=True, type=int)
parser.add_argument('city_from')


def id_check(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        id_check(user_id)
        session = db_session.create_session()
        user = session.query(User).get(User.id)
        return jsonify({
            'user': user.to_dict(only=('name', 'surname', 'position', 'address', 'age', 'city_from'))
        })

    def delete(self, user_id):
        id_check(user_id)
        session = db_session.create_session()
        user = session.query(User).get(User.id).first()
        session.delete(user)
        session.commit()
        return jsonify({'OK': 'Success'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({
            'user': [item.to_dict(only=('name', 'surname', 'position', 'address', 'age', 'city_from')) for item in users]
        })

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            surname=args['surname'],
            user_id=args['id'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            age=args['age'],
            password=generate_password_hash(args['password'])

        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})

