import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from data.hazard import Hazard
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Jobs(SqlAlchemyBase, SerializerMixin):
    serialize_types = (
        (Hazard, lambda x: x.hazard),
    )
    __tablename__ = 'jobs'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    team_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    job = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    collaborators = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    user = orm.relation('User')
    hazard_level = orm.relation('Hazard', secondary="jobs_to_hazard", backref="job")

    def __repr__(self):
        return str(self.id) + ' ' + str(self.job)
