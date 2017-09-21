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


    def messages_in_period(self, from_, to_, channel, nickname=None):
        from_ = datetime.strptime(from_, "%Y.%m.%d %H:%M:%S")
        to_ = datetime.strptime(to_, "%Y.%m.%d %H:%M:%S")
        find_query = {
            'date' : {
                '$gte' : from_,
                '$lte' : to_
            },
            'channel' : channel
        }
        if nickname:
            find_query['login'] = nickname
        return self.database['messages'].find(find_query)
