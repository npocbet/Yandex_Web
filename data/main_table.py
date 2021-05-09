import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class MainTable(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'main'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    n_route_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("routes.id"))
    n_route = orm.relation('Routes')
    begin_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    end_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    up_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    n_st_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("st.id"))
    n_st = orm.relation('Sts')
