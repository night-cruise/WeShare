#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Night Cruising
@File:      test_main.py
@Time:      2021/02/27
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
from flask import url_for

from WeShare.extensions import db
from WeShare.models import User, Notification, Share, Comment, Tag
from .base import BaseTestCase


class MainTestCase(BaseTestCase):

    def test_index_page(self):
        response = self.client.get(url_for('main.index'))
        data = response.get_data(as_text=True)
        self.assertIn('Join Now', data)

        self.login()
        response = self.client.get(url_for('main.index'))
        data = response.get_data(as_text=True)
        self.assertNotIn('Join Now', data)
        self.assertIn('Settings', data)

    def test_explore_page(self):
        response = self.client.get(url_for('main.explore'))
        data = response.get_data(as_text=True)
        self.assertIn('Change', data)

    def test_search(self):
        response = self.client.get(url_for('main.search', q=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Enter keyword about share, user or tag.', data)

        response = self.client.get(url_for('main.search', q='Python Flask'))
        data = response.get_data(as_text=True)
        self.assertNotIn('Enter keyword about share, user or tag.', data)
        self.assertIn('No results.', data)

        response = self.client.get(url_for('main.search', q='Python Flask', category='user'))
        data = response.get_data(as_text=True)
        self.assertNotIn('Enter keyword about share, user or tag.', data)
        self.assertIn('No results.', data)

        response = self.client.get(url_for('main.search', q='Python Flask', category='tag'))
        data = response.get_data(as_text=True)
        self.assertNotIn('Enter keyword about share, user or tag.', data)
        self.assertIn('No results.', data)

    def test_show_notification(self):
        user = User.query.get(2)
        notification1 = Notification(message='test 1', is_read=True, receiver=user)
        notification2 = Notification(message='test 2', is_read=False, receiver=user)
        db.session.add_all([notification1, notification2])
        db.session.commit()

        self.login()
        response = self.client.get(url_for('main.show_notifications'))
        data = response.get_data(as_text=True)
        self.assertIn('test 1', data)
        self.assertIn('test 2', data)

        response = self.client.get(url_for('main.show_notifications', filter='unread'))
        data = response.get_data(as_text=True)
        self.assertNotIn('test 1', data)
        self.assertIn('test 2', data)

    def test_read_notification(self):
        user = User.query.get(2)
        notification1 = Notification(message='test 1', receiver=user)
        notification2 = Notification(message='test 2', receiver=user)
        db.session.add_all([notification1, notification2])
        db.session.commit()

        self.login(email='admin@weshare.com', password='123')
        response = self.client.post(url_for('main.read_notification', notification_id=1))
        self.assertEqual(response.status_code, 403)

        self.logout()
        self.login()

        response = self.client.post(url_for('main.read_notification', notification_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Notification archived.', data)

        self.assertTrue(Notification.query.get(1).is_read)

    def test_read_all_notification(self):
        user = User.query.get(2)
        notification1 = Notification(message='test 1', receiver=user)
        notification2 = Notification(message='test 2', receiver=user)
        db.session.add_all([notification1, notification2])
        db.session.commit()

        self.login()

        response = self.client.post(url_for('main.read_all_notification'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('All notifications archived.', data)

        self.assertTrue(Notification.query.get(1).is_read)
        self.assertTrue(Notification.query.get(2).is_read)

    def test_new_share(self):
        self.login()
        response = self.client.post(url_for('main.new_share'), data=dict(
            title='test title',
            tag='tag1 tag2 tag2',
            body='test body'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Share success.', data)
        self.assertIn('test title', data)
        self.assertIn('tag1', data)
        self.assertIn('tag2', data)

    def test_edit_share(self):
        self.login()
        response = self.client.get(url_for('main.edit_share', share_id=2))
        data = response.get_data(as_text=True)
        self.assertIn('test title 2', data)
        self.assertIn('test body 2', data)

        response = self.client.post(
            url_for('main.edit_share', share_id=2),
            data=dict(title='test edit title', body='test edit body'),
            follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Edit success.', data)
        self.assertIn('test edit title', data)
        self.assertIn('test edit body', data)

    def test_show_share(self):
        response = self.client.get(url_for('main.show_share', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Delete', data)
        self.assertIn('test tag', data)
        self.assertIn('test comment body', data)

        self.login(email='admin@weshare.com', password='123')
        response = self.client.get(url_for('main.show_share', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Delete', data)

    def test_share_next(self):
        user = User.query.get(1)
        share3 = Share(title='test title 3', body='test body 3', author=user)
        share4 = Share(title='test title 4', body='test body 4', author=user)
        share5 = Share(title='test title 5', body='test body 5', author=user)
        db.session.add_all([share3, share4, share5])
        db.session.commit()

        response = self.client.get(url_for('main.share_next', share_id=5), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('test title 4', data)

        response = self.client.get(url_for('main.share_next', share_id=4), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('test title 3', data)

        response = self.client.get(url_for('main.share_next', share_id=3), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('test title 1', data)

        response = self.client.get(url_for('main.share_next', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('This is already the last one.', data)

    def test_share_prev(self):
        user = User.query.get(1)
        share3 = Share(title='test title 3', body='test body 3', author=user)
        share4 = Share(title='test title 4', body='test body 4', author=user)
        share5 = Share(title='test title 5', body='test body 5', author=user)
        db.session.add_all([share3, share4, share5])
        db.session.commit()

        response = self.client.get(url_for('main.share_previous', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('test title 3', data)

        response = self.client.get(url_for('main.share_previous', share_id=3), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('test title 4', data)

        response = self.client.get(url_for('main.share_previous', share_id=4), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('test title 5', data)

        response = self.client.get(url_for('main.share_previous', share_id=5), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('This is already the first one.', data)

    def test_collect(self):
        share = Share(title='test title 3', body='test body 3', author=User.query.get(2))
        db.session.add(share)
        db.session.commit()
        self.assertEqual(Share.query.get(3).collectors, [])

        self.login()
        response = self.client.post(url_for('main.collect', share_id=3), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Share collected.', data)

        self.assertEqual(Share.query.get(3).collectors[0].collector.name, 'Normal User')

        response = self.client.post(url_for('main.collect', share_id=3), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Already collected.', data)

    def test_uncollect(self):
        self.login()
        self.client.post(url_for('main.collect', share_id=1), follow_redirects=True)

        response = self.client.post(url_for('main.uncollect', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Share uncollected.', data)

        response = self.client.post(url_for('main.uncollect', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Not collect yet.', data)

    def test_report_comment(self):
        self.assertEqual(Comment.query.get(1).flag, 0)

        self.login()
        response = self.client.post(url_for('main.report_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment reported.', data)
        self.assertEqual(Comment.query.get(1).flag, 1)

    def test_report_share(self):
        self.assertEqual(Share.query.get(1).flag, 0)

        self.login()
        response = self.client.post(url_for('main.report_share', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Share reported.', data)
        self.assertEqual(Share.query.get(1).flag, 1)

    def test_show_collectors(self):
        user = User.query.get(2)
        user.collect(Share.query.get(1))
        response = self.client.get(url_for('main.show_collectors', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('1 Collectors', data)
        self.assertIn('Normal User', data)

    def test_new_comment(self):
        self.login()
        response = self.client.post(url_for('main.new_comment', share_id=1), data=dict(
            body='test comment from normal user.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)
        self.assertEqual(Share.query.get(1).comments[1].body, 'test comment from normal user.')

    def test_new_tag(self):
        self.login(email='admin@weshare.com', password='123')

        response = self.client.post(url_for('main.new_tag', share_id=1), data=dict(
            tag='hello dog pet happy'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Tag added.', data)
        self.assertEqual(Share.query.get(1).tags[1].name, 'hello')
        self.assertEqual(Share.query.get(1).tags[2].name, 'dog')
        self.assertEqual(Share.query.get(1).tags[3].name, 'pet')
        self.assertEqual(Share.query.get(1).tags[4].name, 'happy')

    def test_set_comment(self):
        self.login()
        response = self.client.post(url_for('main.set_comment', share_id=1), follow_redirects=True)
        self.assertEqual(response.status_code, 403)

        self.logout()
        self.login(email='admin@weshare.com', password='123')
        response = self.client.post(url_for('main.set_comment', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Comment disabled', data)
        self.assertFalse(Share.query.get(1).can_comment)

        response = self.client.post(url_for('main.set_comment', share_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Comment enabled', data)
        self.assertTrue(Share.query.get(1).can_comment)

    def test_reply_comment(self):
        self.login()
        response = self.client.get(url_for('main.reply_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Reply to', data)

    def test_delete_share(self):
        self.login()
        response = self.client.post(url_for('main.delete_share', share_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Share deleted.', data)
        self.assertIn('Normal User', data)

    def test_delete_comment(self):
        self.login()
        response = self.client.post(url_for('main.delete_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment deleted.', data)

    def test_show_tag(self):
        response = self.client.get(url_for('main.show_tag', tag_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Order by time', data)

        response = self.client.get(url_for('main.show_tag', tag_id=1, order='by_collects'))
        data = response.get_data(as_text=True)
        self.assertIn('Order by collects', data)

    def test_delete_tag(self):
        share = Share.query.get(2)
        tag = Tag(name='test')
        share.tags.append(tag)
        db.session.commit()

        self.login()
        response = self.client.post(url_for('main.delete_tag', share_id=2, tag_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Tag deleted.', data)

        self.assertEqual(share.tags, [])
        self.assertIsNone(Tag.query.get(2))
