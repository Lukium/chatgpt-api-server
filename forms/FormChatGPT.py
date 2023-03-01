from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
import settings.Settings as global_settings
import json
with open('./language/{}.json'.format(global_settings.API_LANGUAGE), 'r',encoding="utf-8") as f:
    settings = json.load(f)

from settings.Settings import LANG

LANG = LANG['forms']['chatgpt']

class FormChatGPT(FlaskForm):
    api_key = StringField(label=f'{LANG["labels"]["api_key"]}', validators=[DataRequired()], description=f'{LANG["descriptions"]["api_key"]}')
    prompt = TextAreaField(label=f'{LANG["labels"]["prompt"]}', validators=[DataRequired()])
    conversation_id = StringField(label=f'{LANG["labels"]["conversation_id"]}', description=f'{LANG["descriptions"]["conversation_id"]}')
    plus = SelectField(label=f'{LANG["labels"]["plus"]}', choices=[('any', f'{LANG["choices"]["first_available"]}'), ('true', f'{LANG["choices"]["plus_only"]}'), ('false', f'{LANG["choices"]["free_only"]}')], default='false', description=f'{LANG["descriptions"]["plus"]}')
    reply_only = SelectField(label=f'{LANG["labels"]["reply_only"]}', choices=[('false', f'{LANG["choices"]["no"]}'), ('true', f'{LANG["choices"]["yes"]}')], default='true', description=f'{LANG["descriptions"]["reply_only"]}')
    pretty = SelectField(label=f'{LANG["labels"]["pretty"]}', choices=[('false', f'{LANG["choices"]["no"]}'), ('true', f'{LANG["choices"]["yes"]}')], default='true', description=f'{LANG["descriptions"]["pretty"]}')
    access_token = StringField(label=f'{LANG["labels"]["access_token"]}', description=f'{LANG["descriptions"]["access_token"]}')
    user_plus = SelectField(label=f'{LANG["labels"]["user_plus"]}', choices=[('true', f'{LANG["choices"]["yes"]}'), ('false', f'{LANG["choices"]["no"]}')], default='false', description=f'{LANG["descriptions"]["user_plus"]}')
    submit = SubmitField(label=f'{LANG["labels"]["submit"]}')