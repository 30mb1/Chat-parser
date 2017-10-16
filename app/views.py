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

    #define all forms
    form = forms.chatSetForm()
    comm_form = forms.addCommentForm()
    check_form = forms.checkForm()
    clear_favourite_form = forms.delFavouriteForm()

    messages = []

    #check all forms for submitting

    #form with data and nickname
    if form.submit.data and form.validate_on_submit():
        #store chosen time period in session to save it from request ro request
        session['from'] = datetime.strftime(form.from_date.data, "%Y.%m.%d %H:%M:%S")
        session['to'] = datetime.strftime(form.to_date.data, "%Y.%m.%d %H:%M:%S")
        session['nickname'] = form.nickname.data

    #form for comments
    elif comm_form.submit_comment.data and comm_form.validate_on_submit():
        current_app.database.add_comment(comm_form.data)

    #checkbox form for adding new favourites. Check for add button
    elif check_form.add_check.data and check_form.validate_on_submit():
        current_app.database.add_favourite(request.form)

    #same form but checking for dell button
    elif check_form.dell_check.data and check_form.validate_on_submit():
        current_app.database.dell_favourite(request.form)

    #form for deleting all favourites for channel
    elif clear_favourite_form.clear_submit.data:
        current_app.database.clear_favourite(code)

    #get filters, that we will use for getting messages from db
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

    #check if user is logged in (only admins have accounts)
    #if yes - show all forms and control buttons
    if session.get('logged_in', False):
        return render_template(
                        'index.html',
                        logs=pages,
                        page=page,
                        form=form,
                        form2=comm_form,
                        form3=check_form,
                        form4=clear_favourite_form,
                        cur_username=session['username'],
                        code=code,
                        date=cur_dates
                    )

    #if not, not allow user to write comments to messages and etc.
    return render_template('index.html', logs=pages, page=page, form=form, code=code, date=cur_dates)

@app.route('/report')
def get_report():
    #create temporary file and send it
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


@app.before_first_request
def before_first_request():
    #upload database object to current_app
    current_app.database = Storage()
    return
