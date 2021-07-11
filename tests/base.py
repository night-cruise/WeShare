#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Night Cruising
@File:      base.py
@Time:      2021/02/19
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
import unittest
from typing import Optional

from flask import url_for

from WeShare import create_app
from WeShare.extensions import db
from WeShare.models import Role, User, Share, Tag, Comment


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app('testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        Role.init_role()

        admin_user = User(email='admin@weshare.com', name='Admin', username='admin', confirmed=True)
        admin_user.set_password('123')
        normal_user = User(email='normal@weshare.com', name='Normal User', username='normal', confirmed=True)
        normal_user.set_password('123')
        unconfirmed_user = User(email='unconfirmed@weshare.com', name='Unconfirmed', username='unconfirmed',
                                confirmed=False)
        unconfirmed_user.set_password('123')
        locked_user = User(email='locked@weshare.com', name='Locked User', username='locked',
                           confirmed=True, locked=True)
        locked_user.set_password('123')
        locked_user.lock()

        blocked_user = User(email='blocked@weshare.com', name='Blocked User', username='blocked',
                            confirmed=True, active=False)
        blocked_user.set_password('123')

        share = Share(title='test title 1', body='test body 1', author=admin_user)
        share2 = Share(title='test title 2', body='test body 2', author=normal_user)

        comment = Comment(body='test comment body', share=share, author=normal_user)
        tag = Tag(name='test tag')
        share.tags.append(tag)

        db.session.add_all([admin_user, normal_user, unconfirmed_user, locked_user, blocked_user])
        db.session.commit()

    def login(self, email: Optional[str] = None, password: Optional[str] = None):
        if email is None and password is None:
            email = 'normal@weshare.com'
            password = '123'
        return self.client.post(url_for('auth.login'), data=dict(
            email=email,
            password=password,
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)

    def tearDown(self) -> None:
        db.drop_all()
        self.context.pop()
