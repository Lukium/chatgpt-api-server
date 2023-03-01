from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import settings.Settings as global_settings
import json
with open('./language/{}.json'.format(global_settings.API_LANGUAGE), 'r',encoding="utf-8") as f:
    settings = json.load(f)

from settings.Settings import LANG

LANG = LANG['forms']['chatrecall']

class FormChatRecall(FlaskForm):
    api_key = StringField(label=f'{LANG["labels"]["api_key"]}', validators=[DataRequired()], description=f'{LANG["descriptions"]["api_key"]}')
    conversation_id = StringField(label=f'{LANG["labels"]["conversation_id"]}', description=f'{LANG["descriptions"]["conversation_id"]}')
    submit = SubmitField(label=f'{LANG["labels"]["submit"]}')