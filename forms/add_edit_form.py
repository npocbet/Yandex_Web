from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.fields.html5 import DateTimeField
from wtforms.validators import DataRequired


class AddEditForm(FlaskForm):
    route_number = SelectField(u'Номер рейса', validators=[DataRequired()])
    st_number = SelectField(u'Номер табло', validators=[DataRequired()])
    begin_time = DateTimeField(format='%H:%M', validators=[DataRequired()])
    end_time = DateTimeField(format='%H:%M', validators=[DataRequired()])
    up_time = DateTimeField(format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Изменить')
