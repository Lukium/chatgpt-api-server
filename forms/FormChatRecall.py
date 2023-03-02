from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from settings.Settings import LANG

LANG = LANG['forms']['chatrecall']

class FormChatRecall(FlaskForm):
    api_key = StringField(label=f'{LANG["labels"]["api_key"]}', validators=[DataRequired()], description=f'{LANG["descriptions"]["api_key"]}')
    conversation_id = StringField(label=f'{LANG["labels"]["conversation_id"]}', description=f'{LANG["descriptions"]["conversation_id"]}')
    submit = SubmitField(label=f'{LANG["labels"]["submit"]}')