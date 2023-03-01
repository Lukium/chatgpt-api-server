from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import settings.Settings as global_settings
import json
with open('./language/{}.json'.format(global_settings.API_LANGUAGE), 'r',encoding="utf-8") as f:
    settings = json.load(f)

class FormChatRecall(FlaskForm):
    api_key = StringField(settings['api_key'], validators=[DataRequired()], description=settings['api_key_desc'])
    conversation_id = StringField(settings['conversation_id'], description= settings['FormChatGPT']['conversation_id_desc'])    
    submit = SubmitField(settings['submit'])