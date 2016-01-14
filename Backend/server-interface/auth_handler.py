from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp

from util import log

# minimal setup JWT using Flask-JWT
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

# allowed users.. right now passwords stored as plaintexts, but this is
#   server side, so anyone with access to this could do a lot of damage anyway.
users = [
    User(1, 'rooney', 'suchPass'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)

class AuthHandler:
    def __init__(self, app):
        # Flask-JWT configurations

        # obviously this key needs to be changed for the github releases... (it's gonna be in the commit logs) 
        app.config['SECRET_KEY'] = 'SZE8d9m48#Bg9C76xW3n5#DFQHCpCGZUf9HYll2Wlvs&tPXshr'

        app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
        app.config['JWT_AUTH_PASSWORD_KEY'] = 'password'
        app.config['JWT_AUTH_URL_RULE']     = '/auth/login'

        self.jwt = JWT(app, authenticate, identity)

        self.login_required = jwt_required # for @login_required decorator on routes

        self.current_identity = current_identity
