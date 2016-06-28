# Copyright 2016 The Eyra Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File author/s:
#     Matthias Petursson <oldschool01123@gmail.com>

from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from datetime import timedelta

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
    # change this or add users as you see fit
    User(1, 'rooney@ru.is', 'suchPass'),
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

        # change this..
        app.config['SECRET_KEY'] = 'SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION_SLASH_GITHUB_RELEASE'

        app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
        app.config['JWT_AUTH_PASSWORD_KEY'] = 'password'
        app.config['JWT_AUTH_URL_RULE']     = '/auth/login'
        app.config['JWT_EXPIRATION_DELTA']  = timedelta(days=1)

        self.jwt = JWT(app, authenticate, identity)

        self.login_required = jwt_required # for @login_required decorator on routes

        self.current_identity = current_identity
