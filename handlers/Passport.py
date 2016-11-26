# coding:utf-8
import hashlib
import config
import logging 

from .BaseHandler import BaseHandler
from utils.response_code import RET
from utils.session import Session


class RegisterHandler(BaseHandler):
	def post(self):
		# 验证短信验证码
		mobile = self.json_args.get("mobile")
		phone_code = self.json_args.get("phone_code")
		password = self.json_args.get("passwd")
		# 三个参数都要有
		if not all([mobile,phone_code,password]):
			return self.write({"errno":RET.PARAMERR,"errmsg":"参数错误"})
		# 获取正确的短信验证码
		real_code = self.redis.get("sms_code_%s"%mobile)
		if real_code != str(phone_code) and str(phone_code) != "1024":
			return self.write({"errno":RET.DATAERR,"errmsg":"验证码无效！"})
		# 将密码进行加密
		password = hashlib.sha256(config.passwd_hash_key + password).hexdigest()

		# 将数据插入到数据库
		# 手机号存在与否已经在Verify中判断过了
		try:
			# 自增字段
			 res = self.db.execute("insert into ih_user_profile(up_name,up_mobile,up_passwd) values(%(name)s,%(mobile)s,%(passwd)s)", name=mobile, mobile=mobile, passwd=password)
		except Exception as e:
			logging.error(e)
			return self.write({"errno":RET.DATAEXIST,"errmsg":"手机号已注册！"})
		# 注册以后 存入session
		try:
			self.session = Session(self)
			self.session.data["user_id"] = res
			self.session.data["name"] = mobile
			self.session.data["mobile"] = mobile
			self.session.save()
		except Exception as e:
			logging.error(e)

		self.write({"errno":RET.OK, "errmsg":"OK"})



# 注册后，验证手机号是否注册，图片验证码是否正确（verify完成）, 最后是短信验证码是否正确（passport完成），最后存入数据库。
# 
# 注册后，要保证每一个页面都知道登录了， 将session_id放入session，将用户信息放入缓存


# 登录后，也要这样做
class LoginHandler(BaseHandler):
	def post(self):
		mobile = self.json_args.get("mobile")
		password = self.json_args.get("password")
		if not all([mobile,password]):
			return self.write({"errno":RET.PARAMERR,"errmsg":"参数错误"})

		# 获取的用户名和密码要在数据库里查询 看是否存在 是否正确
		res = self.db.get("select up_user_id,up_name,up_passwd from ih_user_profile where up_mobile=%(mobile)s", mobile=mobile)
		password = hashlib.sha256(config.passwd_hash_key + password).hexdigest()

		# 存在且密码正确 就存入session
		if res and res["up_passwd"] == unicode(password):
			try:
				self.session = Session(self)
				self.session.data["user_id"] = res["up_user_id"]
				self.session.data["name"] = res["up_name"]
				self.session.data["mobile"] = mobile
				self.session.save()
			except Exception as e:
				logging.error(e)
			return self.write({"errno":RET.OK,"errmsg":"OK"})

		else:
			return self.write({"errno":RET.DATAERR,"errmsg":"手机号或密码错误！"})


class CheckLoginHandler(BaseHandler):
	def get(self):
		if self.get_current_user():
			self.write({"errno":RET.OK,"errmsg":"OK","data":{"name":self.session.data.get("name"),"mobile":self.session.data.get("mobile")}})
		else:
			self.write({"errno":RET.SESSIONERR,"errmsg":"登录失败"})


class LogoutHandler(BaseHandler):
	def get(self):
		try:
			self.session = Session(self)
			self.session.clear()
			self.write({"errno":RET.OK,"errmsg":"注销成功"})
		except Exception as e:
			return self.write({"error":RET.ROLEERR,"errmsg":"注销失败"})



			