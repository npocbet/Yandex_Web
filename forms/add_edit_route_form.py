from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class AddEditRouteForm(FlaskForm):
    route = StringField(u'Номер рейса', validators=[DataRequired()])
    path_logo = SelectField(u'Название файла с логотипом', validators=[DataRequired()])
    airport = StringField(u'Аэропорт назначения', validators=[DataRequired()])
    submit = SubmitField('Изменить')
