from app import app, forms
from flask import render_template, request, redirect, url_for, session, current_app, flash, send_from_directory
from datetime import datetime, timedelta, date
from database import Storage
from utils import generate_report
import logging
import os

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
@app.route('/index')
@app.route('/<code>', methods=['GET','POST'])
def index(code='chat_ru'):
    session['code'] = code
    form = forms.chatSetForm()
    comm_form = forms.addCommentForm()
    check_form = forms.checkForm()

    messages = []

    #check all forms for submitting
    if form.submit.data and form.validate_on_submit():
        #store chosen time period in session to save it from request ro request
        session['from'] = datetime.strftime(form.from_date.data, "%Y.%m.%d %H:%M:%S")
        session['to'] = datetime.strftime(form.to_date.data, "%Y.%m.%d %H:%M:%S")
        session['nickname'] = form.nickname.data
    elif comm_form.submit_comment.data and comm_form.validate_on_submit():
        current_app.database.add_comment(comm_form.data)
    elif check_form.submit_check.data and check_form.validate_on_submit():
        current_app.database.add_favourite(request.form)

    filter_args = [session.get('from', None), session.get('to', None), code, session.get('nickname', None)]

    #if user is admin and he wants only favourite messages - add query to filter
    if request.args.get('favourite', False) and session.get('logged_in', False):
        filter_args.append(True)
        session['favourite'] = True
    else:
        session['favourite'] = False

    #get messages from db with specified parameters
    messages = [i for i in current_app.database.messages_in_period(*filter_args)]
    messages = list(reversed(messages))

    #slice messages list for pages
    pages = [messages[i:i + 200] for i in range(0, len(messages), 200)]

    #if no page requested, default to 0
    if request.args.get('page', None):
        page = int(request.args['page'])
    else:
        page = 0

    cur_dates = { 'from' : session.get('from', 'Today'), 'to' : session.get('to', 'Today') }

    #check if it is admin
    #if yes - show comment form
    if session.get('logged_in', False):
        return render_template('index.html', logs=pages, page=page, form=form, form2=comm_form, form3=check_form, cur_username=session['username'], code=code, date=cur_dates)

    #if not, not allow user to write comments to messages
    return render_template('index.html', logs=pages, page=page, form=form, code=code, date=cur_dates)

@app.route('/account',  methods=['GET','POST'])
def account():
    form = forms.udpateAccountForm()

    if form.submit.data and form.validate_on_submit():
        current_app.database.change_username(session['username'], form.username.data)
        session['username'] = form.username.data

    #only admmin can have username in system
    if session.get('logged_in', False):
        return render_template('account.html', form=form, cur_username=session['username'])

    return redirect(url_for('index'))

@app.route('/report')
def get_report():
    generate_report(session)
    try:
        return send_from_directory(
            os.path.join(os.getcwd(), 'tmp'),
            'report.csv',
            as_attachment=True
        )
    except Exception as e:
        print (e)
        return redirect(url_for('index'))

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
    return redirect(url_for('index'))

@app.before_request
def before_request():
    allowed = ['login', 'register']
    if not session.get('logged_in', False) and request.endpoint not in allowed:
        session.pop('username', None)
        session.pop('login', None)

@app.before_first_request
def before_first_request():
    current_app.database = Storage()
    return
