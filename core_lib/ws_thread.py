import threading
import core_lib.redis_pubsub as messaging
from flask_socketio import SocketIO, emit
import traceback
import json
def send_to_ws(msg,arg=None):
    socket_id = msg.get('ws_connection',None)
    if socket_id is None:
        print(f'send_to_ws: No socket id found in event {arg}')
        return
    try:
        print('SCRAPE RESULT')
        print(msg)
        emit(arg, json.dumps(msg), room=socket_id)
        print(f'{arg} event sent successfully to WS {socket_id}')
    except Exception as e:
        print(f'Exception in emitting WS event {arg} to WS {socket_id}')
        print(traceback.format_exc())


class WSEventDispatcher(threading.Thread):
    def __init__(self, event,logger):
        threading.Thread.__init__(self)
        self.daemon = True
        self.event = event
        self.pubsub = messaging.PubSub(logger=logger)
        self.pubsub.subscribe(event)
        print(f'WS_DISPATCHER THREAD INITIALIZED for event: {event}')
       
    def run(self):
        self.pubsub.listen_for_events_forever(handler=send_to_ws,arg=self.event)