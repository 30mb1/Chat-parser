from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, IntegerField, SelectField, StringField, TextField, DateField
from wtforms.validators import Required, Optional


class chatSetForm(FlaskForm):
    from_date = DateField('From', [Required()])
    to_date = DateField('To', [Required()])
    channel = SelectField('Channel', choices=[('chat_en', 'en'), ('chat_ru', 'ru'), ('chat_cn', 'cn')])
    nickname = TextField('Nickname')
    submit = SubmitField('Show')

class addCommnetForm(FlaskForm):
    from_user = StringField('Username')
    comment = StringField('Comment', [Required()])
    msg_id = StringField('msg_id')
    submit_comment = SubmitField('Add')

class udpateAccountForm(FlaskForm):
    username = StringField('Username', [Required()])
    submit = SubmitField('Update')
