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
    print (form.data)

    messages = []

    if form.validate_on_submit():
        from_ = form.from_date.data
        to_ = form.to_date.data
        channel = form.channel.data

        session['from'] = from_
        session['to'] = to_
        session['channel'] = channel


    messages = [i for i in current_app.database.messages_in_period(session['from'], session['to'], session['channel'])]

    return render_template('index.html', logs=reversed(messages), form=form)

@app.before_first_request
def before_first_request():
    current_app.database = Storage()
    today = datetime.combine(date.today(), datetime.min.time())
    session['from'] = today
    session['to'] = today + timedelta(days=1)
    session['channel'] = 'chat_ru'
    return
