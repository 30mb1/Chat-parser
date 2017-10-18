from pymongo import MongoClient
from datetime import datetime, timedelta, date
import html

class Storage(object):
    def __init__(self):
        self.database = MongoClient()['wex_chat_parser']

    def username_exist(self, username):
        return self.database['accounts'].find_one(
            {
                'username' : username
            }
        )

    def login_exist(self, login):
        return self.database['accounts'].find_one(
            {
                'login' : login
            }
        )

    def get_account(self, login):
        return self.database['accounts'].find_one(
            {
                'login' : login
            }
        )

    def register_new_account(self, data):
        if self.login_exist(data['login']):
            return 'This login is already taken.'

        if self.username_exist(data['username']):
            return 'This username is already taken.'

        data.pop('csrf_token', None)

        self.database['accounts'].insert_one(data)

        return True

    def change_username(self, cur_name, new_name):
        return self.database['accounts'].update_one(
            {
                'username' : cur_name
            },
            {
                '$set' : {
                    'username' : new_name
                }
            }
        )

    def check_auth(self, login, password):
        return self.database['accounts'].find_one(
            {
                'login' : login,
                'password' : password
            }
        )

    def save_message(self, data, channel):
        data['msg'] = html.unescape(data['msg'])
        data['channel'] = channel
        data['date'] = datetime.utcnow()
        self.database['messages'].update_one(
            {
                'msg_id' : data['msg_id'],
                'uid' : data['uid'],
                'channel' :channel
            },
            {
                '$setOnInsert' : data
            },
            upsert=True
        )

    def get_message_by_id(self, msg_id):
        return self.database['messages'].find_one(
            { 'msg_id' : int(msg_id) }
        )

    def add_favourite(self, data, user):
        values_list = []
        logs = []

        for num in data.getlist('msg_id'):
            values_list.append(int(num))

            msg = self.get_message_by_id(int(num))
            logs.append(
                {
                    'action' : 'add',
                    'login' : user,
                    'msg' : msg['msg'],
                    'msg_date' : msg['date'],
                    'msg_user' : msg['login'],
                    'date' : datetime.utcnow()
                }
            )

        self.database['history'].insert_many(logs)

        values_list = [int(num) for num in data.getlist('msg_id')]
        self.database['messages'].update_many(
            {
                'msg_id' : { '$in' : values_list }
            },
            {
                '$set' : {
                    'favourite' : True
                }
            }
        )
    def dell_favourite(self, data, user):
        values_list = []
        logs = []

        for num in data.getlist('msg_id'):
            values_list.append(int(num))

            msg = self.get_message_by_id(int(num))
            logs.append(
                {
                    'action' : 'del',
                    'login' : user,
                    'msg' : msg['msg'],
                    'msg_date' : msg['date'],
                    'msg_user' : msg['login'],
                    'date' : datetime.utcnow()
                }
            )

        self.database['history'].insert_many(logs)

        self.database['messages'].update_many(
            {
                'msg_id' : { '$in' : values_list }
            },
            {
                '$set' : {
                    'favourite' : False
                }
            }
        )

    def clear_favourite(self, from_, to_, code, user):
        # clear all favourite in given period
        if from_ == None or to_ == None:
            #if no input, return current day
            today = datetime.combine(date.today(), datetime.min.time())
            next_day = today + timedelta(days=1)
            from_ = datetime.strftime(today, "%Y.%m.%d %H:%M:%S")
            to_ = datetime.strftime(next_day, "%Y.%m.%d %H:%M:%S")

        from_ = datetime.strptime(from_, "%Y.%m.%d %H:%M:%S")
        to_ = datetime.strptime(to_, "%Y.%m.%d %H:%M:%S")

        self.database['history'].insert_one(
            {
                'action' : 'clear',
                'channel' : code,
                'login' : user,
                'date' : datetime.utcnow(),
                'from' : from_,
                'to' : to_
            }
        )

        self.database['messages'].update_many(
            {
                'favourite' : True,
                'channel' : code,
                'date' : {
                    '$gte' : from_,
                    '$lte' : to_
                }
            },

            {
                '$set' : {
                    'favourite' : False
                }
            }
        )

    def add_comment(self, data):
        username = data['from_user'] if data['from_user'] != '' else 'Anonymous'
        self.database['comments'].insert_one(
            {
                'text' : data['comment'],
                'username' : username,
                'msg_id' : int(data['msg_id']),
                'date' : datetime.utcnow()
            }
        )


    def messages_in_period(self, from_, to_, channel='chat_ru', nickname=None, favourite=None):
        if from_ == None or to_ == None:
            #if no input, return current day
            today = datetime.combine(date.today(), datetime.min.time())
            next_day = today + timedelta(days=1)
            from_ = datetime.strftime(today, "%Y.%m.%d %H:%M:%S")
            to_ = datetime.strftime(next_day, "%Y.%m.%d %H:%M:%S")

        from_ = datetime.strptime(from_, "%Y.%m.%d %H:%M:%S")
        to_ = datetime.strptime(to_, "%Y.%m.%d %H:%M:%S")

        join_query = {
            '$lookup' : {
                'from' : 'comments',
                'localField' : 'msg_id',
                'foreignField' : 'msg_id',
                'as' : 'comments'
            }
        }

        find_query = {
            '$match' : {
                'date' : {
                    '$gte' : from_,
                    '$lte' : to_
                },
                'channel' : channel
            }
        }

        if nickname:
            find_query['$match']['login'] = nickname
        if favourite:
            find_query['$match']['favourite'] = True

        return self.database['messages'].aggregate([find_query, join_query])
