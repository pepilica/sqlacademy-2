from flask import Flask, render_template, redirect, request
from flask_login import LoginManager
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField
from flask_restful import reqparse, abort, Api, Resource
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from data import db_session
from data.jobs import Jobs
from data.users import User
from data.departments import Departments
from flask_wtf import FlaskForm
from flask_login import login_user, login_required, logout_user, current_user
import users_resource


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
user_api = Api(app)

user_api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')
user_api.add_resource(users_resource.UsersListResource, '/api/v2/users')


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
    submit = SubmitField('Submit')


class CreateJobForm(FlaskForm):
    job = StringField('Job name', validators=[DataRequired()])
    team_leader = IntegerField('Team leader ID', validators=[DataRequired()])
    collaborators = StringField('Collaborators')
    work_size = IntegerField('Work size')
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
        if user0:
            job = Jobs(
                job=form.job.data,
                team_leader=form.team_leader.data,
                collaborators=form.collaborators.data,
                is_finished=form.is_finished.data,
                work_size=form.work_size.data
            )
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
        else:
            abort(403)
    if form.validate_on_submit():
        session = db_session.create_session()
        job = session.query(Jobs).filter(Jobs.id == id,
                                         ((Jobs.user == current_user) | (current_user.id == 1))).first()
        user = session.query(User).filter(User.id == int(form.team_leader.data)).all()
        if job:
            if user:
                job.job = form.job.data
                job.team_leader = form.team_leader.data
                job.collaborators = form.collaborators.data
                job.is_finished = form.is_finished.data
                job.work_size = form.work_size.data
                session.commit()
                return redirect('/')
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


if __name__ == '__main__':
    db_session.global_init("db/mars.sqlite")

    app.run(port=8080, host='127.0.0.1')