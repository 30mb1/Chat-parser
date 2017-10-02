from pymongo import MongoClient
from datetime import datetime


class Storage(object):
    def __init__(self):
        self.database = MongoClient()['wex_chat_parser']

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
            return []
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
