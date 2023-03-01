from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
import settings.Settings as global_settings
import json
with open('./language/{}.json'.format(global_settings.API_LANGUAGE), 'r',encoding="utf-8") as f:
    settings = json.load(f)

class FormChatGPT(FlaskForm):
    api_key = StringField(settings['api_key'], validators=[DataRequired()], description=settings['api_key_desc'])    
    prompt = TextAreaField(settings['FormChatGPT']['prompt'], validators=[DataRequired()])
    conversation_id = StringField(settings['conversation_id'], description=settings['FormChatGPT']['conversation_id_desc'])
    plus = SelectField(label=settings['FormChatGPT']['plus'], choices=[('any', settings['FormChatGPT']['plus_any']), ('true', settings['FormChatGPT']['plus_true']), ('false', settings['FormChatGPT']['plus_false'])], default='false', description=settings['FormChatGPT']['plus_desc'])
    reply_only = SelectField(settings['FormChatGPT']['reply_only'], description=settings['FormChatGPT']['reply_only_desc'], choices=[('false', settings['false']), ('true', settings['true'])], default='false')
    pretty = SelectField(settings['FormChatGPT']['pretty'], description=settings['FormChatGPT']['reply_only_desc'], choices=[('false', settings['false']), ('true', settings['true'])], default='true')    
    access_token = StringField(settings['FormChatGPT']['access_token'], description=settings['FormChatGPT']['access_token_desc'])
    user_plus = SelectField(label=settings['FormChatGPT']['user_plus'], choices=[('true', settings['true']), ('false', settings['false'])], default='false', description=settings['FormChatGPT']['user_plus_desc'])
    submit = SubmitField(settings['submit'])