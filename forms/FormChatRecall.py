from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class FormChatRecall(FlaskForm):
    api_key = StringField('API Key', validators=[DataRequired()], description=f'OVERRIDEN IF PASSED VIA URL [user=] . Lukium Swarm API Key, NOT OpeanAI API Key')
    conversation_id = StringField('Conversation ID', description= "If NOT passed, will retrieve a list of all conversations' IDs and their titles. If PASSED, will retrieve the conversation's title and all messages' IDs, prompts and replies.")    
    submit = SubmitField('Submit')