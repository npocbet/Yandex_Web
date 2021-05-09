from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class AddEditStForm(FlaskForm):
    remote_ip = StringField(u'Адрес табло', validators=[DataRequired()])
    type = SelectField(u'Тип табло', validators=[DataRequired()])
    submit = SubmitField('Изменить')
