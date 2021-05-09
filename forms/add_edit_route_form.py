from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddEditRouteForm(FlaskForm):
    route = StringField(u'Номер рейса', validators=[DataRequired()])
    path_logo = StringField(u'Номер рейса', validators=[DataRequired()])
    airport = StringField(u'Номер рейса', validators=[DataRequired()])
    submit = SubmitField('Изменить')
