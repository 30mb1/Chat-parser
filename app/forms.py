from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, SelectField, StringField, DateTimeField, PasswordField, BooleanField
from wtforms.validators import Required, Optional


class chatSetForm(FlaskForm):
    from_date = DateTimeField('From', format='%Y-%m-%d %H:%M', validators=[Required()])
    to_date = DateTimeField('To', format='%Y-%m-%d %H:%M', validators=[Required()])
    nickname = StringField('Nickname')
    submit = SubmitField('Show')

class addCommentForm(FlaskForm):
    from_user = StringField('Username')
    comment = StringField('Comment', [Required()])
    msg_id = StringField('msg_id')
    submit_comment = SubmitField('Add')

class udpateAccountForm(FlaskForm):
    username = StringField('Username', [Required()])
    submit = SubmitField('Update')

class LoginForm(FlaskForm):
    login = StringField('Login', [Required()])
    password = PasswordField('Password', [Required()])

class RegisterForm(FlaskForm):
    username = StringField('Username', [Required()])
    password = PasswordField('Password', [Required()])
    login = StringField('Login', [Required()])

class checkForm(FlaskForm):
    msg_id = IntegerField('msg_id')
    submit_check = SubmitField('Add favourite')
