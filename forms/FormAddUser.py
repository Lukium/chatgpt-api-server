from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import settings.Settings as global_settings
import json
with open('./language/{}.json'.format(global_settings.API_LANGUAGE), 'r',encoding="utf-8") as f:
    settings = json.load(f)

class FormAddUser(FlaskForm):
    plus = SelectField(label=settings['FormAddUser']['plus'], validators=[DataRequired()], choices=[('true', settings['true']), ('false', settings['false'])], default='false', description=settings['FormAddUser']['plus_desc'])
    is_client = SelectField(label=settings['FormAddUser']['is_client'], validators=[DataRequired()], choices=[('true', settings['true']), ('false', settings['false'])], default='false', description=settings['FormAddUser']['is_client_desc'])
    userid = StringField(settings['FormAddUser']['userid'], validators=[DataRequired()], description=settings['FormAddUser']['userid_desc'])
    username = StringField(settings['FormAddUser']['username'], validators=[DataRequired()], description=settings['FormAddUser']['username_desc'])
    submit = SubmitField(settings['submit'])