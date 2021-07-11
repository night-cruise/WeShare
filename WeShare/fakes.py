#!/user/bin/python
# -*-coding:UTF-8-*-
"""
@Author:    Night Cruising
@File:      fakes.py
@Time:      2021/02/18
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from WeShare.extensions import db
from WeShare.models import User, Share, Tag, Comment, Notification

fake = Faker()


def fake_admin():
    admin = User(
        name='Admin User',
        username='adminuser',
        email='admin@weshare.com',
        bio=fake.sentence(),
        website='http://example.com',
        confirmed=True
    )
    admin.set_password('weshare')
    notification = Notification(message='Hello, welcome to WeShare.', receiver=admin)
    db.session.add(admin)
    db.session.add(notification)
    db.session.commit()


def fake_user(count=20):
    for i in range(count):
        user = User(
            name=fake.name(),
            confirmed=True,
            username=fake.user_name(),
            bio=fake.sentence(),
            website=fake.url(),
            member_since=fake.date_time_this_year(),
            email=fake.email(),
            location=fake.city(),
        )
        user.set_password('123456')
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_follow(count=60):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.follow(User.query.get(random.randint(1, user.query.count())))
    db.session.commit()


def fake_tag(count=20):
    for i in range(count):
        tag = Tag(name=fake.word())
        db.session.add(tag)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_share(count=60):
    for i in range(count):
        share = Share(
            title=fake.sentence(),
            body=fake.text(),
            author=User.query.get(random.randint(1, User.query.count()))
        )
        for j in range(random.randint(1, 5)):
            tag = Tag.query.get(random.randint(1, Tag.query.count()))
            share.tags.append(tag)
        db.session.add(share)
    db.session.commit()


def fake_collect(count=60):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.collect(Share.query.get(random.randint(1, Share.query.count())))
    db.session.commit()


def fake_comment(count=150):
    for i in range(count):
        comment = Comment(
            author=User.query.get(random.randint(1, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            share=Share.query.get(random.randint(1, Share.query.count()))
        )
        db.session.add(comment)
    db.session.commit()
