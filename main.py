from io import BytesIO

import requests
from PIL import Image
from flask import Flask, render_template, redirect, request, jsonify
from flask_login import LoginManager
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField
from flask_restful import reqparse, abort, Api, Resource
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data import db_session
from data.jobs import Jobs
from data.hazard import Hazard
from data.hazard import association_table
from data.users import User
from data.departments import Departments
from flask_wtf import FlaskForm
from flask_login import login_user, login_required, logout_user, current_user
from requests import get
import users_resource
import jobs_resource
import jobs_api
import users_api
from get_coords import get_bbox

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
user_api = Api(app)

user_api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')
user_api.add_resource(users_resource.UsersListResource, '/api/v2/users')
user_api.add_resource(jobs_resource.JobsResource, '/api/v2/jobs/<int:job_id>')
user_api.add_resource(jobs_resource.JobsListResource, '/api/v2/jobs')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class DepartmentForm(FlaskForm):
    title = StringField('Department title', validators=[DataRequired()])
    chief = IntegerField('Department chief', validators=[DataRequired()])
    members = StringField('Members')
    email = EmailField('Department mail', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    email = EmailField('Login/E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    city_from = StringField('Hometown')
    submit = SubmitField('Submit')


class CreateJobForm(FlaskForm):
    job = StringField('Job name', validators=[DataRequired()])
    team_leader = IntegerField('Team leader ID', validators=[DataRequired()])
    collaborators = StringField('Collaborators')
    work_size = IntegerField('Work size')
    hazard_level = IntegerField('Hazard category (1 - 10)')
    is_finished = BooleanField('Is finished?')
    submit = SubmitField('Submit')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/departments')
def departments():
    session = db_session.create_session()
    return render_template('departments.html', data=session.query(Departments),
                           session=session, User=User, title='Departments',
                           current_user=current_user)


@app.route('/add_department', methods=['POST', 'GET'])
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user0 = session.query(User).filter(User.id == form.chief.data).all()
        if user0:
            department = Departments(
                title=form.title.data,
                chief=form.chief.data,
                members=form.members.data,
                email=form.email.data
            )
            session.merge(current_user)
            session.add(department)
            session.commit()
            return redirect("/departments")
        else:
            return render_template('department_submit.html', title='Department add', form=form,
                                   message='Team leader does not exists',
                                   action='Adding a Department')
    return render_template('department_submit.html', title='Department add', form=form, action='Adding a Department')


@app.route('/departments/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    form = DepartmentForm()
    if request.method == "GET":
        session = db_session.create_session()
        department = session.query(Departments).filter(Departments.id == id,
                                                       ((Departments.user == current_user) |
                                                        (current_user.id == 1))).first()
        if department:
            form.title.data = department.title
            form.chief.data = department.chief
            form.members.data = department.members
            form.email.data = department.email
        else:
            abort(403)
    if form.validate_on_submit():
        session = db_session.create_session()
        department = session.query(Departments).filter(Departments.id == id,
                                                       ((Departments.user == current_user) |
                                                        (current_user.id == 1))).first()
        user = session.query(User).filter(User.id == form.chief.data).all()
        if department:
            if user:
                department.title = form.title.data
                department.chief = form.chief.data
                department.members = form.members.data
                department.email = form.email.data
                session.commit()
                return redirect('/departments')
            else:
                return render_template('department_submit.html', title='Department edit', form=form,
                                       message='Team leader does not exists', action='Editing a Department')
        else:
            abort(403)
    return render_template('department_submit.html', title='Department edit', form=form, action='Editing a Department')


@app.route('/departments_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def departments_delete(id):
    session = db_session.create_session()
    department = session.query(Departments).filter(Departments.id == id,
                                                   ((Departments.user == current_user) |
                                                    (current_user.id == 1))).first()
    if department:
        session.delete(department)
        session.commit()
    else:
        abort(403)
    return redirect('/departments')


@app.route('/index')
@app.route('/')
def jobs():
    session = db_session.create_session()
    return render_template('jobs.html', data=session.query(Jobs), session=session, User=User, title='Jobs',
                           current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="Password did not match")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        if form.city_from.data:
            user.city_from = form.city_from.data
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/')
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Wrong password",
                               form=form)
    return render_template('login.html', title='Login', form=form)


@app.route('/addjob', methods=['POST', 'GET'])
def add_job():
    form = CreateJobForm()
    print(current_user)
    if form.validate_on_submit():
        session = db_session.create_session()
        user0 = session.query(User).filter(User.id == form.team_leader.data).all()
        if current_user.id != form.team_leader.data and current_user.id != 1:
            return render_template('job_submit.html', title='Job add', form=form, message='Operation forbidden',
                                   action='Adding a Job')
        elif user0:
            job = Jobs(
                job=form.job.data,
                team_leader=form.team_leader.data,
                collaborators=form.collaborators.data,
                is_finished=form.is_finished.data,
                work_size=form.work_size.data,
            )
            possible = session.query(Hazard).filter(Hazard.hazard == form.hazard_level.data).first()
            if not possible:
                session.add(Hazard(hazard=form.hazard_level.data))
                possible = session.query(Hazard).filter(Hazard.hazard == form.hazard_level.data).first()
                print(possible)
            job.hazard_level.append(possible)
            session.merge(current_user)
            session.add(job)
            session.commit()
            return redirect("/")
        else:
            return render_template('job_submit.html', title='Job add', form=form, message='Team leader does not exists',
                                   action='Adding a Job')
    return render_template('job_submit.html', title='Job edit', form=form, action='Adding a Job')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = CreateJobForm()
    if request.method == "GET":
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == id,
                                         ((Jobs.user == current_user) | (current_user.id == 1))).first()
        if job:
            form.job.data = job.job
            form.team_leader.data = job.team_leader
            form.collaborators.data = job.collaborators
            form.is_finished.data = job.is_finished
            form.work_size.data = job.work_size
            if job.hazard_level:
                form.hazard_level.data = job.hazard_level[0].hazard
        else:
            abort(403)
    if form.validate_on_submit():
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == id,
                                         ((Jobs.user == current_user) | (current_user.id == 1))).first()
        user = session.query(User).filter(User.id == form.team_leader.data).all()
        if job:
            if current_user.id != form.team_leader.data and current_user.id != 1:
                return render_template('job_submit.html', title='Job edit', form=form, message='Operation forbidden',
                                       action='Editing a Job')
            elif user:
                job.job = form.job.data
                job.team_leader = form.team_leader.data
                job.collaborators = form.collaborators.data
                job.is_finished = form.is_finished.data
                job.work_size = form.work_size.data
                if job.hazard_level:
                    job.hazard_level.remove(job.hazard_level)
                possible = session.query(Hazard).filter(Hazard.hazard == form.hazard_level.data).first()
                if not possible:
                    session.add(Hazard(hazard=form.hazard_level.data))
                    possible = session.query(Hazard).filter(Hazard.hazard == form.hazard_level.data).first()
                job.hazard_level.append(possible)
                session.commit()
                return redirect('/')
            elif current_user.id != form.team_leader.data and current_user.id != 1:
                return render_template('job_submit.html', title='Job edit', form=form, message='Operation forbidden',
                                       action='Adding a Job')
            else:
                return render_template('job_submit.html', title='Job edit', form=form,
                                       message='Team leader does not exists', action='Editing a Job')
        else:
            abort(403)
    return render_template('job_submit.html', title='Job edit', form=form, action='Editing a Job')


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    session = db_session.create_session()
    job = session.query(Jobs).filter(Jobs.id == id,
                                     ((Jobs.user == current_user) | (current_user.id == 1))).first()
    if job:
        session.delete(job)
        session.commit()
    else:
        abort(403)
    return redirect('/')


@app.route('/users_show/<int:user_id>')
def users_show(user_id):
    user = get(f'http://127.0.0.1:8080/api/users/{user_id}').json()
    if 'error' in user.keys():
        abort(404)
    else:
        name, surname = user['user']['name'], user['user']['surname']
        city_from = user['user']['city_from']
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": city_from,
            "format": "json"
        }
        response = requests.get('http://geocode-maps.yandex.ru/1.x/', params=geocoder_params)

        json_response = response.json()
        print(json_response)
        if json_response and not 'error' in json_response.keys():
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"]
            if toponym:
                toponym = toponym[0]["GeoObject"]
                toponym_coodrinates = toponym["Point"]["pos"]
                info = toponym['boundedBy']['Envelope']
                toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
                map_params = {
                    "ll": ",".join([toponym_longitude, toponym_lattitude]),
                    "l": "sat",
                    'bbox': get_bbox(info)
                }
                response = requests.get('http://static-maps.yandex.ru/1.x/', params=map_params).url
                print(response)
                return render_template('nostalgy.html', url=response, name=name, surname=surname,
                                       city_from=city_from, title='Nostalgy')
        return render_template('nostalgy.html', url='', name=name, surname=surname,
                               city_from=city_from, title='Nostalgy')


if __name__ == '__main__':
    db_session.global_init("db/mars.sqlite")
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
