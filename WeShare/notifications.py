#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Night Cruising
@File:      notifications.py
@Time:      2021/02/18
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
from flask import url_for

from WeShare.extensions import db
from WeShare.models import Notification


def push_follow_notification(follower, receiver):
    message = 'User <a href="%s">%s</a> followed you.' % \
              (url_for('user.index', username=follower.username), follower.username)
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_comment_notification(share_id, receiver, page=1):
    message = '<a href="%s#comments">This share</a> has new comment/reply.' % \
              (url_for('main.show_share', share_id=share_id, page=page))
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_collect_notification(collector, share_id, receiver):
    message = 'User <a href="%s">%s</a> collected your <a href="%s">share</a>' % \
              (url_for('user.index', username=collector.username),
               collector.username,
               url_for('main.show_share', share_id=share_id))
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()
