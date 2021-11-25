import json
import redis
import config
from redis_connection import connect_to_server
import hashlib
import uuid
from datetime import datetime
from core_lib.platform_utils import get_event_hash
from core_lib.redis_lock import LockTask
import traceback

class KeyValueStore():
    def __init__(self,server,logger):
        try:
            self.server = server
            self.logger = logger
        except Exception as e:
            raise

    def insert(self,key,value,logger):
        server = self.server
        #logger.debug(key,value)
        #server.hmset(key, value)
        server.hset("tasks", key, value)

         
    def get(self,key,logger):
        server = self.server
        #logger.debug(key)
        #val = server.hgetall(key)
        val = server.hget('tasks',key)
        return val
    
    def getall(self,logger):
        server = self.server
        keys = server.hgetall('tasks')
        return keys

    def remove(self,key,logger):
        server = self.server
        logger.debug('removing key {}'.format(key))
        server.hdel('tasks',key)
        logger.debug('key {} removed'.format(key))
        


class PubSub():
    def __init__(self,logger):
        try:
            self.server = connect_to_server(logger)
            self.logger = logger
            self.pubsub = self.server.pubsub(ignore_subscribe_messages=True)
            self.locker = LockTask(logger)
            self.kv_store = KeyValueStore(self.server,logger)
        except:
            raise


    def subscribe(self,event_type):
        self.pubsub.subscribe(event_type)
        self.logger.debug('subscribed to event_type={}'.format(event_type))

    def publish(self, event, event_type):
        logger = self.logger
        taskid = str(uuid.uuid1().hex[:16])
        try:
            self.locker.create_lock(taskid)
            event['taskid'] = taskid    
        except Exception as e:
            logger.error(f'unable to create lock error = {e}')
            logger.error(traceback.format_exc())
              
        self.server.publish(event_type, json.dumps(event))
        self.logger.debug(f'published event_type={event_type}')
        #print(f'^^^^^^^^^^^^^^^^^^^PUBLISHED EVENT TYPE = {event_type} ')
        
    def start_event(self,event):
        taskid = event.get('taskid',None)
        if taskid is None:
            return None
        acquired = self.locker.get_lock(taskid)
        if not acquired:
            return None
        #self.locker.remove_lock(taskid)
        return event
    
    def stop_event(self,event):
        taskid = event.get('taskid',None)
        if taskid is None:
            return
        #self.locker.remove_lock(taskid)
        del event['taskid']
        
    
    def cleanup(self,minutes=60):
        logger = self.logger
        count = 0
        try:
            keys = self.kv_store.getall(logger)
            now = datetime.now().timestamp()
            for key in keys:
                val = self.kv_store.get(key,logger)
                if (now - float(val))//60 >= minutes:
                    self.kv_store.remove(key,logger)
                    count = count + 1
            if count > 0:
                print(f'{count} events cleanedup')
        except Exception as e:
            logger.error('failed with error {}'.format(e))
            raise Exception('cleanup failed with error {}'.format(e))
        
        
    def listen_for_events_forever(self,handler=None,arg=None):
        self.logger.debug('entering')
        self.handler = handler
        for m in self.pubsub.listen():
            if self.handler is not None:
                #data = m['data']
                #data2 = json.loads(m['data'])
                #print(f'LISTEN FOR EVENTS: TYPE OF DATA = {type(data)}')
                #print(f'LISTEN FOR EVENTS: TYPE OF DATA2 = {type(data2)}')
                self.handler(json.loads(m['data']),arg=m['channel'])
        self.logger.debug('leaving')


