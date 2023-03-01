from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import settings.Settings as global_settings
import json
with open('./language/{}.json'.format(global_settings.API_LANGUAGE), 'r',encoding="utf-8") as f:
    settings = json.load(f)

from settings.Settings import LANG

LANG = LANG['forms']['add_user']

class FormAddUser(FlaskForm):
    plus = SelectField(label=f'{LANG["labels"]["plus"]}', validators=[DataRequired()], choices=[('true', f'{LANG["choices"]["yes"]}'), ('false', f'{LANG["choices"]["no"]}')], default='false', description=f'{LANG["descriptions"]["plus"]}')
    is_client = SelectField(label=f'{LANG["labels"]["is_client"]}', validators=[DataRequired()], choices=[('true', f'{LANG["choices"]["yes"]}'), ('false', f'{LANG["choices"]["no"]}')], default='false', description=f'{LANG["descriptions"]["is_client"]}')
    userid = StringField(label=f'{LANG["labels"]["userid"]}', validators=[DataRequired()], description=f'{LANG["descriptions"]["userid"]}')
    username = StringField(label=f'{LANG["labels"]["username"]}', validators=[DataRequired()], description=f'{LANG["descriptions"]["username"]}')
    submit = SubmitField(label=f'{LANG["labels"]["submit"]}')