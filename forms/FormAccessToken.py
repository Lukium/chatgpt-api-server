from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
import settings.Settings as global_settings
import json
with open('./language/{}.json'.format(global_settings.API_LANGUAGE), 'r',encoding="utf-8") as f:
    settings = json.load(f)

class FormAccessToken(FlaskForm):
    api_key = StringField(settings['api_key'], validators=[DataRequired()], description=settings['api_key_desc'])
    email = StringField(settings['FromAccessToken']['email'], validators=[DataRequired()], description=settings['FromAccessToken']['email_desc'])
    password = PasswordField(settings['FromAccessToken']['password'], validators=[DataRequired()], description=settings['FromAccessToken']['password_desc'])
    submit = SubmitField(settings['submit'])