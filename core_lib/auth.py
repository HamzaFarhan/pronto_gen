from abc import ABC, abstractmethod
from flask_login import UserMixin

class AuthService(ABC):

	def load_user(self,email):
		pass

	def get_redirect_uri(self,request):
		pass

	def authenticate_user(self,request,login_func):
		pass
	def logout_user(self,user,logout_func):
		pass
    
	def check_user_token(self,user):
		pass

class AuthUser(UserMixin):
    def __init__(self,email,session_id,token):
        self.email = email
        self.auth_token = token
        self.session_id = session_id
    def get_id(self):
        return self.email
    
    