from app import app, forms
from flask import render_template, request, redirect, url_for, session, current_app, flash, send_from_directory
from datetime import datetime, timedelta, date
import time
from database import Storage
import logging
import threading
from multiprocessing import Process

logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    form = forms.chatSetForm()
    comm_form = forms.addCommnetForm()
    #print (form.data)

    messages = []

    if form.submit.data and form.validate_on_submit():

        from_ = datetime.combine(form.from_date.data, datetime.min.time())
        to_ = datetime.combine(form.to_date.data, datetime.min.time())

        session['from'] = datetime.strftime(from_, "%Y.%m.%d %H:%M:%S")
        session['to'] = datetime.strftime(to_, "%Y.%m.%d %H:%M:%S")
        session['channel'] = form.channel.data
        session['nickname'] = form.nickname.data
    elif comm_form.submit_comment.data and comm_form.validate_on_submit():
        current_app.database.add_comment(comm_form.data)


    messages = [i for i in current_app.database.messages_in_period(session.get('from', None), session.get('to', None), session.get('channel', 'chat_ru'), session.get('nickname', None))]
    messages = list(reversed(messages))
    pages = [messages[i:i + 200] for i in range(0, len(messages), 200)]

    if request.args.get('page', None):
        page = int(request.args['page'])
    else:
        page = 0

    return render_template('index.html', logs=pages, page=page, form=form, form2=comm_form)

@app.before_first_request
def before_first_request():
    current_app.database = Storage()
    return
