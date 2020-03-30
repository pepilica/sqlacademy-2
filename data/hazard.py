import sqlalchemy
from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table('jobs_to_hazard', SqlAlchemyBase.metadata,
    sqlalchemy.Column('job', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('jobs.id')),
    sqlalchemy.Column('hazard', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('hazards.id'))
)


class Hazard(SqlAlchemyBase):
    __tablename__ = 'hazards'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    hazard = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return self.hazard
