from app import forms
from flask import render_template, request, redirect, url_for, session, current_app, Blueprint

user_pages = Blueprint('user_pages', __name__,
                        template_folder='templates')

@user_pages.route('/account',  methods=['GET','POST'])
def account():
    form = forms.udpateAccountForm()

    #form for changing username
    if form.submit.data and form.validate_on_submit():
        current_app.database.change_username(session['username'], form.username.data)
        session['username'] = form.username.data

    return render_template('account.html', form=form, cur_username=session['username'])


@user_pages.route('/login', methods=['GET','POST'])
def login():
    form = forms.LoginForm()

    #if user logged in successfully, store his data in session
    if form.validate_on_submit():
        if current_app.database.check_auth(form.login.data, form.password.data):
            session['logged_in'] = True
            session['username'] = current_app.database.get_account(form.login.data)['username']
            session['login'] = form.login.data
            return redirect(url_for('index'))

    return render_template('login.html', form=form)


@user_pages.route('/register', methods=['GET','POST'])
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


@user_pages.route('/logout')
def logout():
    #remove all data from user session if he logged out
    session.clear()
    return redirect(url_for('index'))

#check for user being logged in
#this is for cases when session time ended
@user_pages.before_request
def before_request():
    allowed = ['login', 'register']
    if not session.get('logged_in', False) and request.endpoint not in allowed:
        session.pop('username', None)
        session.pop('login', None)
