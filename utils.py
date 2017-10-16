from database import Storage
from pandas.io.json import json_normalize
from datetime import datetime
import html


def generate_report(session):
    s = Storage()
    filter_args = [session.get('from', None),
                   session.get('to', None),
                   session.get('code', None),
                   session.get('nickname', None),
                   session.get('favourite', None)]


    messages = []
    for msg in s.messages_in_period(*filter_args):

        messages.append(
            {
                'date' : msg['date'],
                'channel' : msg['channel'],
                'login' : msg['login'],
                'message' : html.unescape(msg['msg']),
                'comments' : [
                    {
                        'user' : comm['username'],
                        'text' : comm['text']
                    } for comm in msg['comments']
                ]
            }
        )
    messages = list(reversed(messages))

    filename = './tmp/report.csv'

    res = json_normalize(messages)
    res.to_csv(filename)
