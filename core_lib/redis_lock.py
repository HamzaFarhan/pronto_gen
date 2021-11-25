
import json
import redis
import config
from redis_connection import connect_to_server
from datetime import timedelta
class LockTask():
    def __init__(self,logger):
        try:
            self.server = connect_to_server(logger)
            self.logger = logger
        except Exception as e:
            raise

    def create_lock(self,taskid):
        server = self.server
        #server.setex(taskid, timedelta(minutes=10),value="false")
        server.set(taskid,"false")
        
    def get_lock(self,taskid):
        server = self.server
        if server.get(taskid):
            if server.getset(taskid,"true") != "false":
                return False
            #server.expire(taskid, timedelta(minutes=10))
            return True
        return False
    

    def remove_lock(self,taskid):
        server = self.server
        server.delete(taskid)
        