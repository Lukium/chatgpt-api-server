from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
import settings.Settings as global_settings
import json
with open('./language/{}.json'.format(global_settings.API_LANGUAGE), 'r',encoding="utf-8") as f:
    settings = json.load(f)

from settings.Settings import LANG

LANG = LANG['forms']['access_token']

class FormAccessToken(FlaskForm):
    api_key = StringField(label=f'{LANG["labels"]["api_key"]}', validators=[DataRequired()], description=f'{LANG["descriptions"]["api_key"]}')
    email = StringField(label=f'{LANG["labels"]["email"]}', validators=[DataRequired()], description=f'{LANG["descriptions"]["email"]}')
    password = PasswordField(label=f'{LANG["labels"]["password"]}', validators=[DataRequired()], description=f'{LANG["descriptions"]["password"]}')
    submit = SubmitField(label=f'{LANG["labels"]["submit"]}')