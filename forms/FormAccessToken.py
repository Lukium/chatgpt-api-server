from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

class FormAccessToken(FlaskForm):
    api_key = StringField('API Key', validators=[DataRequired()], description=f'OVERRIDEN IF PASSED VIA URL [user=] . Lukium Swarm API Key, NOT OpeanAI API Key')
    email = StringField('ChatGPT Email', validators=[DataRequired()], description= "Your OpenAI ChatGPT Email. This is the email that you use to login to the OpenAI ChatGPT website.")
    password = PasswordField('ChatGPT Password', validators=[DataRequired()], description="Your OpenAI ChatGPT Password. This is the password that you use to login to the OpenAI ChatGPT website.")
    submit = SubmitField('Submit')