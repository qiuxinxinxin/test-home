# coding:utf-8
import uuid
import logging
import json
import config

class Session(object):
	def __init__(self,request_handler):
		self.request_handler = request_handler
		# 获取session_id
		self.session_id = self.request_handler.get_secure_cookie("session_id")
		# 获取不到session_id，用户第一次访问
		if not self.session_id:
			# 生成一个session_id
			self.session_id = uuid.uuid4().get_hex()
			self.data = {}
		else:
		# 获取到了session_id,去redis中取数据
			try:
				data = self.request_handler.redis.get("sess_%s" %self.session_id)
			except Exception as e:
				logging.error(e)
				self.data = {}
				
			if not data:
				self.data = {}
			else:
				self.data = json.loads(data)
		 
	def save(self):
		json_data = json.dumps(self.data)
		try:
			# 缓存中存的是key是session_id 一个uuid
			# value 是包括user_id user_name mobile在内的json
			
			self.request_handler.redis.setex("sess_%s" %self.session_id,config.session_expires,json_data)
		except Exception as e:
			logging.error(e)
			raise Exception("save session failed")
			# session中只存了session_id
		else:
			self.request_handler.set_secure_cookie("session_id", self.session_id)

	def clear(self):
		self.request_handler.clear_cookie("session_id")
		try:
			self.request_handler.redis.delete("sess_%s" %self.session_id)
		except Exception as e:
			logging.error(e)


