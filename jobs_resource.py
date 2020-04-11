from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource

from data.hazard import Hazard
from data.users import User, generate_password_hash
from data.jobs import Jobs
from data import db_session


parser = reqparse.RequestParser()
parser.add_argument('team_leader', required=True, type=int)
parser.add_argument('job', required=True)
parser.add_argument('work_size', required=True, type=int)
parser.add_argument('collaborators', required=True)
parser.add_argument('is_finished', required=True, type=bool)
parser.add_argument('hazard_level', required=True, type=int)


def id_check_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


def id_check_job(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, message=f"Job {job_id} not found")


class JobsResource(Resource):
    def get(self, job_id):
        id_check_job(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({
            'user': job.to_dict(only=('team_leader', 'job', 'work_size', 'collaborators', 'is_finished',
                                      'hazard_level'))
        })

    def delete(self, job_id):
        id_check_job(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id).first()
        session.delete(job)
        session.commit()
        return jsonify({'OK': 'Success'})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({
            'job': [item.to_dict(only=('team_leader', 'job', 'work_size', 'collaborators', 'is_finished',
                                       'hazard_level')) for item in jobs]
        })

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        id_check_user(args['team_leader'])
        job = Jobs(
            team_leader=args['team_leader'],
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            is_finished=args['is_finished']
        )
        possible = session.query(Hazard).filter(Hazard.hazard == args['hazard_level']).first()
        if not possible:
            session.add(Hazard(hazard=args['hazard_level']))
            possible = session.query(Hazard).filter(Hazard.hazard == args['hazard_level']).first()
        job.hazard_level.append(possible)
        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})
