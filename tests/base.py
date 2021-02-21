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

from WeShare import create_app
from WeShare.extensions import db

class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app('testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    def tearDown(self) -> None:
        db.drop_all()
        self.context.pop()