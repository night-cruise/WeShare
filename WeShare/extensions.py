#!/user/bin/python
# -*-coding:UTF-8-*-
"""
@Author:    Night Cruising
@File:      extensions.py
@Time:      2021/02/18
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
from flask_bootstrap import Bootstrap
from flask_avatars import Avatars
from flask_ckeditor import CKEditor
from flask_mail import Mail
from flask_whooshee import Whooshee
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, AnonymousUserMixin
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf import CSRFProtect

bootstrap = Bootstrap()
avatars = Avatars()
mail = Mail()
ckeditor = CKEditor()
moment = Moment()
whooshee = Whooshee()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
debugtoolbar = DebugToolbarExtension()

@login_manager.user_loader
def load_user(user_id):
    from WeShare.models import User
    user = User.query.get(int(user_id))
    return user

login_manager.login_view = 'auth.login'

login_manager.login_message_category = 'warning'

login_manager.refresh_view = 'auth.re_authenticate'

login_manager.needs_refresh_message_category = 'warning'

class Guest(AnonymousUserMixin):
    def can(self, permission_name):
        return False

    @property
    def is_admin(self):
        return False

login_manager.anonymous_user = Guest