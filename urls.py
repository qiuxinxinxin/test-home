# coding:utf-8
from handlers import Passport,VerifyCode,Profile
from tornado.web import StaticFileHandler
import os

handlers = [
	(r"^/api/verifycode",VerifyCode.ImageCodeHandler),
	(r"^/api/smscode",VerifyCode.SMSCodeHandler),
	(r"^/api/register",Passport.RegisterHandler),
	(r"^/api/login",Passport.LoginHandler),
	(r"^/api/check_login",Passport.CheckLoginHandler),
	(r"^/api/profile",Passport.CheckLoginHandler),
	(r"^/api/logout",Passport.LogoutHandler),
	(r"^/api/profile/avatar",Profile.AvatarHandler),  #上传保存头像
	(r"/(.*)", StaticFileHandler, dict(path=os.path.join(os.path.dirname(__file__), "html"), default_filename="index.html"))
]