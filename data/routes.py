import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Routes(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'routes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    route = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    path_logo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    airport = sqlalchemy.Column(sqlalchemy.String, nullable=True)
