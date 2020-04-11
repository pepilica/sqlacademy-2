import flask
from flask import jsonify, request
from data import db_session
from data.hazard import Hazard
from data.jobs import Jobs

blueprint = flask.Blueprint('jobs_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/jobs', methods=['GET'])
def get_jobs():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('job', 'user.name', 'user.surname', 'collaborators', 'work_size', 'is_finished',
                                    'start_date', 'end_date', 'hazard_level'))
                 for item in jobs]
        }
    )


@blueprint.route('/api/jobs/<job_id>', methods=['GET'])
def get_one_job(job_id):
    try:
        job_id = int(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        if not job:
            return jsonify({'error': 'Not found'})
        return jsonify(
            {
                'job': job.to_dict(only=('job', 'user.name', 'user.surname', 'collaborators', 'work_size',
                                         'is_finished', 'start_date', 'end_date', 'hazard_level'))
            }
        )
    except ValueError:
        return jsonify({'error': 'Not found'})


@blueprint.route('/api/jobs/', methods=['POST'])
def create_job():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['job', 'team_leader', 'collaborators', 'work_size', 'is_finished', 'hazard_level']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    if 'id' in request.json:
        if session.query(Jobs).get(Jobs.id == request.json['id']):
            return jsonify({'error': 'Id already exists'})
    job = Jobs(
        job=request.json['job'],
        team_leader=request.json['team_leader'],
        collaborators=request.json['collaborators'],
        is_finished=request.json['is_finished'],
        work_size=request.json['work_size'],
    )
    possible = session.query(Hazard).filter(Hazard.hazard == request.json['hazard_level']).first()
    if not possible:
        session.add(Hazard(hazard=request.json['hazard_level']))
        possible = session.query(Hazard).filter(Hazard.hazard == request.json['hazard_level']).first()
    job.hazard_level.append(possible)
    session.add(job)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    session = db_session.create_session()
    try:
        job_id = int(job_id)
        job = session.query(Jobs).get(job_id)
        if not job:
            return jsonify({'error': 'Not found'})
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})
    except ValueError:
        return jsonify({'error': 'Not found'})


@blueprint.route('/api/jobs/<job_id>', methods=['PUT'])
def edit_job(job_id):
    session = db_session.create_session()
    try:
        job_id = int(job_id)
        job = session.query(Jobs).get(job_id)
        if not job:
            return jsonify({'error': 'Not found'})
    except ValueError:
        return jsonify({'error': 'Not found'})
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not any(key in request.json for key in
                 ['job', 'team_leader', 'collaborators', 'work_size', 'is_finished', 'hazard_level']):
        return jsonify({'error': 'Bad request'})
    job.job = request.json['job']
    job.team_leader = request.json['team_leader']
    job.collaborators = request.json['collaborators']
    job.is_finished = request.json['is_finished']
    job.work_size = request.json['work_size']
    if job.hazard_level:
        job.hazard_level.remove(job.hazard_level[0])
    possible = session.query(Hazard).filter(Hazard.hazard == request.json['hazard_level']).first()
    if not possible:
        session.add(Hazard(hazard=request.json['hazard_level']))
        possible = session.query(Hazard).filter(Hazard.hazard == request.json['hazard_level']).first()
    job.hazard_level.append(possible)
    session.commit()
    return jsonify({'success': 'OK'})
