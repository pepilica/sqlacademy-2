import flask
from flask import jsonify, request
from data import db_session
from data.users import User

blueprint = flask.Blueprint('users_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/users', methods=['GET'])
def get_jobs():
    session = db_session.create_session()
    users = session.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('name', 'surname', 'speciality', 'position', 'address', 'email',
                                    'jobs', 'departments', 'city_from'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<user_id>', methods=['GET'])
def get_one_job(user_id):
    try:
        user_id = int(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'Not found'})
        return jsonify(
            {
                'user': user.to_dict(only=('name', 'surname', 'speciality', 'position', 'address', 'email',
                                     'jobs', 'departments', 'city_from'))
            }
        )
    except ValueError:
        return jsonify({'error': 'Not found'})


@blueprint.route('/api/users/', methods=['POST'])
def create_job():
    try:
        if not request.json:
            return jsonify({'error': 'Empty request'})
        elif not all(key in request.json for key in
                     ['name', 'surname', 'speciality', 'position', 'address', 'email',
                      'password', 'age']):
            return jsonify({'error': 'Bad request'})
        session = db_session.create_session()
        if 'id' in request.json:
            if session.query(User).get(User.id == request.json['id']):
                return jsonify({'error': 'Id already exists'})
        user = User(
            name=request.json['name'],
            surname=request.json['surname'],
            speciality=request.json['speciality'],
            position=request.json['position'],
            address=request.json['address'],
            email=request.json['email'],
            age=request.json['age']
        )
        if 'city_from' in request.json.keys():
            user.city_from = request.json['city_from']
        user.set_password(request.json['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
    except Exception:
        return jsonify({'error': 'Bad request'})


@blueprint.route('/api/users/<user_id>', methods=['DELETE'])
def delete_job(user_id):
    session = db_session.create_session()
    try:
        user_id = int(user_id)
        user = session.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'Not found'})
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})
    except ValueError:
        return jsonify({'error': 'Not found'})


@blueprint.route('/api/users/<user_id>', methods=['PUT'])
def edit_job(user_id):
    session = db_session.create_session()
    try:
        user_id = int(user_id)
        user = session.query(User).get(user_id)
        if not user:
            return jsonify({'error': 'Not found'})
        if not request.json:
            return jsonify({'error': 'Empty request'})
        elif not all(key in request.json for key in
                     ['name', 'surname', 'speciality', 'position', 'address', 'email',
                      'password', 'age']):
            return jsonify({'error': 'Bad request'})
        user.name = request.json['job']
        user.surname = request.json['surname']
        user.speciality = request.json['speciality']
        user.position = request.json['position']
        user.address = request.json['address']
        user.email = request.json['email']
        user.age = request.json['age']
        if 'city_from' in request.json['city_from']:
            user.city_from = request.json['city_from']
        user.set_password(request.json['password'])
        session.commit()
        return jsonify({'success': 'OK'})
    except ValueError:
        return jsonify({'error': 'Not found'})
    except Exception:
        return jsonify({'error': 'Bad request'})
