from app import app
from flask import render_template, request, redirect, url_for, session, current_app, flash, send_from_directory
from datetime import datetime, timedelta, date
from forms import chatSetForm
import time
from database import Storage
import logging
import threading
from multiprocessing import Process

logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
    form = chatSetForm()
    #print (form.data)

    messages = []

    if form.submit.data and form.validate_on_submit():

        from_ = datetime.combine(form.from_date.data, datetime.min.time())
        to_ = datetime.combine(form.to_date.data, datetime.min.time())

        session['from'] = datetime.strftime(from_, "%Y.%m.%d %H:%M:%S")
        session['to'] = datetime.strftime(to_, "%Y.%m.%d %H:%M:%S")
        session['channel'] = form.channel.data
        session['nickname'] = form.nickname.data

    messages = [i for i in current_app.database.messages_in_period(session.get('from', '0.0.0 0:0:0'), session.get('to', '0.0.0 0:0:0'), session.get('channel', 'chat_ru'), session.get('nickname', None))]

    return render_template('index.html', logs=reversed(messages), form=form)

@app.before_first_request
def before_first_request():
    current_app.database = Storage()
    today = datetime.combine(date.today(), datetime.min.time())
    next_day = today + timedelta(days=1)
    session['from'] = datetime.strftime(today, "%Y.%m.%d %H:%M:%S")
    session['to'] = datetime.strftime(next_day, "%Y.%m.%d %H:%M:%S")
    session['channel'] = 'chat_ru'
    session['nickname'] = ''
    return
