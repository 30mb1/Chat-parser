# -*- coding: utf-8 -*-
import websocket
import threading
import time
import json
import logging
from database import Storage

s = Storage()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger('Main')

chat_ru = { "event" : "pusher:subscribe", "data" : { "channel" : 'chat_ru' } }
chat_en = { "event" : "pusher:subscribe", "data" : { "channel" : 'chat_en' } }
chat_cn = { "event" : "pusher:subscribe", "data" : { "channel" : 'chat_cn' } }


def on_message(ws, message):
    message = json.loads(message)

    if message['event'] == 'pusher:connection_established' or message['event'] == 'pusher_internal:subscription_succeeded':
        print (message)
        return

    channel = message['channel']
    print (type(message['data']))
    message = json.loads(message['data'])
    message = json.loads(message)

    if 'msg' in message.keys():
        s.save_message(message, channel)
        logger.info(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    ws.close()
    print("### closed ###")

def on_open(ws):
    def run(*args):
        print ('New thread for listening started.')
        ws.send(json.dumps(chat_ru))
        ws.send(json.dumps(chat_en))
        ws.send(json.dumps(chat_cn))
    t = threading.Thread(target=run(), args=())
    t.start()

while True:
    try:
        ws = websocket.WebSocketApp("ws://ws-eu.pusher.com:80/app/ee987526a24ba107824c?protocol=7",
                                  on_message = on_message,
                                  on_error = on_error,
                                  on_close = on_close)
        ws.on_open = on_open
        ws.run_forever(ping_interval=5, ping_timeout=1)
    except Exception as e:
        print (e)
        pass
    time.sleep(5)
