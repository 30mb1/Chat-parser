from app import app, forms
from flask import render_template, request, redirect, url_for, session, current_app, flash, send_from_directory
from datetime import datetime, timedelta, date
from database import Storage
import logging

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
@app.route('/index')
@app.route('/<code>', methods=['GET','POST'])
def index(code='chat_ru'):

    form = forms.chatSetForm()
    comm_form = forms.addCommnetForm()

    messages = []

    if form.submit.data and form.validate_on_submit():

        session['from'] = datetime.strftime(form.from_date.data, "%Y.%m.%d %H:%M:%S")
        session['to'] = datetime.strftime(form.to_date.data, "%Y.%m.%d %H:%M:%S")
        session['nickname'] = form.nickname.data
    elif comm_form.submit_comment.data and comm_form.validate_on_submit():
        current_app.database.add_comment(comm_form.data)

    messages = [i for i in current_app.database.messages_in_period(session.get('from', None), session.get('to', None), code, session.get('nickname', None))]
    messages = list(reversed(messages))
    pages = [messages[i:i + 200] for i in range(0, len(messages), 200)]

    if request.args.get('page', None):
        page = int(request.args['page'])
    else:
        page = 0

    cur_dates = { 'from' : session.get('from', 'Today'), 'to' : session.get('to', 'Today') }
    return render_template('index.html', logs=pages, page=page, form=form, form2=comm_form, cur_username=session['username'], code=code, date=cur_dates)

@app.route('/account',  methods=['GET','POST'])
def account():
    form = forms.udpateAccountForm()

    if form.submit.data and form.validate_on_submit():
        current_app.database.change_username(session['username'], form.username.data)
        session['username'] = form.username.data

    return render_template('account.html', form=form, cur_username=session['username'])


@app.route('/login', methods=['GET','POST'])
def login():
    form = forms.LoginForm()

    if form.validate_on_submit():
        if current_app.database.check_auth(form.login.data, form.password.data):
            session['logged_in'] = True
            session['username'] = current_app.database.get_account(form.login.data)['username']
            session['login'] = form.login.data
            return redirect(url_for('index'))

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    return 'disabled'
    form = forms.RegisterForm()

    error = None
    if form.validate_on_submit():
        res = current_app.database.register_new_account(form.data)
        if res == True:
            return redirect(url_for('login'))
        else:
            error = res

    return render_template('registration.html', form=form, error=error)

@app.route('/logout')
def logout():
    session.clear()

    return redirect(url_for('login'))

@app.before_request
def before_request():
    allowed = ['login', 'register']
    if not session.get('logged_in', False) and request.endpoint not in allowed:
        return redirect(url_for('login'))

@app.before_first_request
def before_first_request():
    current_app.database = Storage()
    return
