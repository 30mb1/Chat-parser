from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectField, StringField, DateTimeField
from wtforms.validators import Required, Optional


class chatSetForm(FlaskForm):
    from_date = DateTimeField('From', format='%Y-%m-%d %H:%M', validators=[Required()])
    to_date = DateTimeField('To', format='%Y-%m-%d %H:%M', validators=[Required()])
    channel = SelectField('Channel', choices=[('chat_en', 'en'), ('chat_ru', 'ru'), ('chat_cn', 'cn')])
    nickname = StringField('Nickname')
    submit = SubmitField('Show')

class addCommnetForm(FlaskForm):
    from_user = StringField('Username')
    comment = StringField('Comment', [Required()])
    msg_id = StringField('msg_id')
    submit_comment = SubmitField('Add')

class udpateAccountForm(FlaskForm):
    username = StringField('Username', [Required()])
    submit = SubmitField('Update')
