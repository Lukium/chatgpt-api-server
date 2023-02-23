from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class FormChatGPT(FlaskForm):
    api_key = StringField('Lukium Swarm API Key', validators=[DataRequired()], description=f'OVERRIDEN IF PASSED VIA URL [user=] . Lukium Swarm API Key, NOT OpeanAI API Key')    
    prompt = TextAreaField('Prompt', validators=[DataRequired()])
    conversation_id = StringField('Conversation ID', description='OPTIONAL - Used to continue a conversation. If not provided, a new conversation will be started.')
    plus = SelectField(label='Use Plus or Free?', choices=[('any', 'First Available'), ('true', 'Plus Only'), ('false', 'Free Only')], default='false', description='Use Plus or Free (Plus only available for Premium+ Supporters)')
    reply_only = SelectField('Reply Only?', description='Get only the reply, not the full JSON response', choices=[('false', 'No'), ('true', 'Yes')], default='true')
    pretty = SelectField('Markdown Reply?', description='Ignored if "Reply Only" = "No" | Use markdown styling (prettier) for the response?', choices=[('false', 'No'), ('true', 'Yes')], default='true')    
    access_token = StringField('OpenAI Access Token', description=f'OPTIONAL - OVERRIDEN IF PASSED VIA URL [access_token=] . OpenAI Access Token, NOT Lukium Swarm API Key. Can be retrieved using /access-token endpoint')
    user_plus = SelectField(label='OpenAI Plus?', choices=[('true', 'Yes'), ('false', 'No')], default='false', description='Does this access token have OpenAI Plus?')
    submit = SubmitField('Submit')