#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Night Cruising
@File:      test_cli.py
@Time:      2021/02/19
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
from WeShare.extensions import db
from WeShare.models import Comment, Role, User, Share, Tag
from tests.base import BaseTestCase

class CliTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(CliTestCase, self).setUp()
        db.drop_all()

    def test_initdb_command(self):
        result = self.runner.invoke(args=['initdb'])
        self.assertIn('Initialized database.', result.output)

    def test_initdb_command_with_drop(self):
        result = self.runner.invoke(args=['initdb', '--drop'], input='y\n')
        self.assertIn('This operation will delete the database, do you want to continue?', result.output)
        self.assertIn('Drop tables.', result.output)

    def test_init_command(self):
        result = self.runner.invoke(args=['init'])
        self.assertIn('Initializing the database...', result.output)
        self.assertIn('Initializing the roles and permissions...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(Role.query.count(), 4)

    def test_forge_command(self):
        result = self.runner.invoke(args=['forge'])

        self.assertIn('Initializing the roles and permissions...', result.output)
        self.assertEqual(Role.query.count(), 4)

        self.assertEqual(User.query.count(), 21)
        self.assertIn('Generating the administrator...', result.output)
        self.assertIn('Generating 20 users...', result.output)

        self.assertIn('Generating 60 follows...', result.output)

        self.assertEqual(Share.query.count(), 60)
        self.assertIn('Generating 60 shares...', result.output)

        self.assertEqual(Tag.query.count(), 20)
        self.assertIn('Generating 20 tags...', result.output)

        self.assertIn('Generating 60 collects...', result.output)

        self.assertEqual(Comment.query.count(), 150)
        self.assertIn('Generating 150 comments...', result.output)

        self.assertIn('Done.', result.output)

    def test_forge_command_with_count(self):
        result = self.runner.invoke(args=['forge', '--user', '5', '--follow', '10',
                                          '--share', '10', '--tag', '10', '--collect', '10',
                                          '--comment', '10'])

        self.assertIn('Initializing the roles and permissions...', result.output)

        self.assertEqual(User.query.count(), 6)
        self.assertIn('Generating the administrator...', result.output)
        self.assertIn('Generating 5 users...', result.output)

        self.assertIn('Generating 10 follows...', result.output)

        self.assertEqual(Share.query.count(), 10)
        self.assertIn('Generating 10 shares...', result.output)

        self.assertEqual(Tag.query.count(), 10)
        self.assertIn('Generating 10 tags...', result.output)

        self.assertIn('Generating 10 collects...', result.output)

        self.assertEqual(Comment.query.count(), 10)
        self.assertIn('Generating 10 comments...', result.output)

        self.assertIn('Done.', result.output)
