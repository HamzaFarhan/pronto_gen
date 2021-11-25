
import json
import redis
import config
from redis_connection import connect_to_server

class KeyValueStore():
	def __init__(self,logger):
		try:
			self.server = connect_to_server(logger)
			self.logger = logger
		except Exception as e:
			raise

	def insert(self,key,value,logger):
		server = self.server
		logger.debug(key,value)
		server.hmset(key, value)

	def get(self,key,logger):
		server = self.server
		logger.debug(key)
		try:
			val = server.hgetall(key)
		except Exception as e:
			logger.error("unable to retrieve value of key {} from Redis: error = {}".format(key,e))
			raise "unable to retrieve value of key {} from Redis: error = {}".format(key,e)
		logger.debug('retrieved value {} against key {}'.format(val,key))
		return val

	def getall(self):
		return self.server.keys()

	def remove(self,key,logger):
		server = self.server
		logger.debug('removing key {}'.format(key))
		try:
			all_keys = list(server.hgetall(key).keys())
			server.hdel(key, *all_keys)
			logger.debug('key {} removed'.format(key))
		except Exception as e:
			logger.error("unable to remove key {} from Redis: error = {}".format(key,e))
			raise "unable to remove key {} from Redis: error = {}".format(key,e)
