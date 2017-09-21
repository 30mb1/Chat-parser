from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, IntegerField, SelectField, StringField, TextAreaField, DateField
from wtforms.validators import Required, Optional


class chatSetForm(FlaskForm):
    from_date = DateField('From', [Required()])
    to_date = DateField('To', [Required()])
    channel = SelectField('Channel', choices=[('chat_en', 'en'), ('chat_ru', 'ru'), ('chat_cn', 'cn')])
    submit = SubmitField('Show')
