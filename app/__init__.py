from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.secret_key = '`\xbb>\xb2[\xcdJA\\X\xa1\xb2\xdb\x9c\x17\x80/;\xe6\x05\xb4\xf0\xa4\xb5'
app.wsgi_app = ProxyFix(app.wsgi_app)

from app import views
