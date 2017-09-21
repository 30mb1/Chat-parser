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


    def messages_in_period(self, from_, to_, channel):
        from_ = datetime.combine(from_, datetime.min.time())
        to_ = datetime.combine(to_, datetime.min.time())
        return self.database['messages'].find(
            {
                'date' : {
                    '$gte' : from_,
                    '$lte' : to_
                },
                'channel' : channel
            }
        )
