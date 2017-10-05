from pymongo import MongoClient
from datetime import datetime, timedelta, date


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


    def messages_in_period(self, from_, to_, channel, nickname=None):
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

        return self.database['messages'].aggregate([find_query, join_query])
