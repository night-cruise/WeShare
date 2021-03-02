#!/user/bin/python
# -*-coding:UTF-8-*-
"""
@Author:    Night Cruising
@File:      settings.py
@Time:      2021/02/18
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQlite URI
WIN = sys.platform.startswith('win')
prefix = 'sqlite:///' if WIN else 'sqlite:////'

class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'

class BaseConfig(object):
    WESHARE_ADMIN_EMAIL = os.getenv('WESHAER_EMAIL', 'admin@weshare.com')
    WESHARE_SHARE_PER_PAGE = 15
    WESHARE_COMMET_PER_PAGE = 15
    WESHARE_NOTIFICATION_PER_PAGE = 20
    WESHARE_USER_PER_PAGE = 20
    WESHARE_MANAGE_SHARE_PER_PAGE = 20
    WESHARE_MANAGE_USER_PER_PAGE = 30
    WESHARE_MANAGE_TAG_PER_PAGE = 50
    WESHARE_MANAGE_COMMENT_PER_PAGE = 30
    WESHARE_SEARCH_RESULT_PER_PAGE = 20
    WESHARE_MAIL_SUBJECT_PREFIX = '[WeShare]'

    WESHARE_UPLOAD_PATH = os.path.join(BASE_DIR, 'uploads')
    WESHARE_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024

    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_FILE_UPLOADER = 'main.upload_image'

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    BOOTSTRAP_SERVE_LOCAL = True

    CACHE_TYPE = 'redis'

    WESHARE_SLOW_QUERY_THRESHOLD = 1
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AVATARS_SAVE_PATH = os.path.join(WESHARE_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE = (30, 100, 200)

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('WeShare Admin', MAIL_USERNAME)

    WHOOSHEE_MIN_STRING_LEN = 1

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(BASE_DIR, 'data-dev.db')

class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'  # in-memory database

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        prefix + os.path.join(BASE_DIR, 'data.db')
    )

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}