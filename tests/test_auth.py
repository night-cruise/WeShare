#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Night Cruising
@File:      test_auth.py
@Time:      2021/02/22
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
from flask import url_for

from WeShare.helpers import generate_token
from WeShare.models import User
from WeShare.settings import Operations

from tests.base import BaseTestCase


class AuthTestCase(BaseTestCase):

    def test_login_normal_user(self):
        response = self.login()
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)

    def test_login_locked_user(self):
        self.login(email='locked@weshare.com', password='123')
        pass

    def test_login_blocked_user(self):
        response = self.login(email='blocked@weshare.com', password='123')
        data = response.get_data(as_text=True)
        self.assertIn('Your account is blocked.', data)

    def test_fail_login(self):
        response = self.login(email='wrong-username@weshare.com', password='wrong-password')
        data = response.get_data(as_text=True)
        self.assertIn('Invalid email or password.', data)

    def test_logout_user(self):
        self.login()
        response = self.logout()
        data = response.get_data(as_text=True)
        self.assertIn('Logout success.', data)

    def test_login_protect(self):
        pass

    def test_unconfirmed_user_permission(self):
        pass

    def test_locked_user_permission(self):
        pass

    def test_register_account(self):
        response = self.client.post(url_for('auth.register'), data=dict(
            name='Weshare',
            email='test@helloflask.com',
            username='weshare',
            password='12345678',
            password2='12345678'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Confirm email sent, check your inbox.', data)

    def test_confirm_account(self):
        user = User.query.filter_by(email='unconfirmed@weshare.com').first()
        self.assertFalse(user.confirmed)
        token = generate_token(user=user, operation='confirm')
        self.login(email='unconfirmed@weshare.com', password='123')
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Account confirmed.', data)
        self.assertTrue(user.confirmed)

    def test_bad_confirm_token(self):
        self.login(email='unconfirmed@weshare.com', password='123')
        response = self.client.get(url_for('auth.confirm', token='bad token'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid or expired token.', data)
        self.assertNotIn('Account confirmed.', data)

    def test_reset_password(self):
        response = self.client.post(url_for('auth.forget_password'), data=dict(
            email='normal@weshare.com',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Password reset email sent, check your inbox.', data)
        user = User.query.filter_by(email='normal@weshare.com').first()
        self.assertTrue(user.validate_password('123'))

        token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
        response = self.client.post(url_for('auth.reset_password', token=token), data=dict(
            email='normal@weshare.com',
            password='new-password',
            password2='new-password'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Password updated.', data)
        self.assertTrue(user.validate_password('new-password'))
        self.assertFalse(user.validate_password('123'))

        # bad token
        response = self.client.post(url_for('auth.reset_password', token='bad token'), data=dict(
            email='normal@weshare.com',
            password='new-password',
            password2='new-password'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid or expired link.', data)
        self.assertNotIn('Password updated.', data)