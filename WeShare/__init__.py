#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Night Cruising
@File:      __init__.py.py
@Time:      2021/02/18
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
import os
import click
from flask import Flask, render_template, current_app
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from flask_sqlalchemy import get_debug_queries

from WeShare.views.admin import admin_bp
from WeShare.views.user import user_bp
from WeShare.views.main import main_bp
from WeShare.views.auth import auth_bp
from WeShare.views.ajax import ajax_bp
from WeShare.extensions import bootstrap, db, login_manager, \
    mail, moment, whooshee, avatars, csrf, debugtoolbar, ckeditor
from WeShare.models import Role, User, Share, Tag, Follow, \
    Notification, Comment, Collect, Permission
from WeShare.settings import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_template_context(app)
    register_errorhandlers(app)
    register_commands(app)
    register_request_handlers(app)

    return app

def register_request_handlers(app):
    @app.after_request
    def query_profiler(response):
        for q in get_debug_queries():
            if q.duration >= current_app.config['WESHARE_SLOW_QUERY_THRESHOLD']:
                current_app.logger.warning(
                    'Slow query: Duration: %f\n Context: %s\nQuery: %s\b'%(
                        q.duration, q.context, q.statement
                    )
                )

        return response

def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    whooshee.init_app(app)
    avatars.init_app(app)
    csrf.init_app(app)
    debugtoolbar.init_app(app)
    ckeditor.init_app(app)

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ajax_bp, url_prefix='/ajax')

def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(
            db=db, User=User, Share=Share, Tag=Tag,
            Follow=Follow, Collect=Collect, Comment=Comment,
            Notification=Notification, Role=Role
        )

def register_template_context(app):
    @app.context_processor
    def make_template_context():
        if current_user.is_authenticated:
            notification_count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
        else:
            notification_count = 0
        return dict(notification_count=notification_count)

def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 500

def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    def init():
        """Initialize WeShare."""
        click.echo('Initializing the database...')
        db.drop_all()
        db.create_all()
        click.echo("Initializing the roles and permissions...")
        Role.init_role()

        click.echo('Done.')

    @app.cli.command()
    @click.option('--user', default=20, help='Quantity of users, default is 20.')
    @click.option('--follow', default=60, help='Quantity of follows, default is 30.')
    @click.option('--share', default=60, help='Quantity of shares, default is 60.')
    @click.option('--tag', default=20, help='Quantity of tags, default is 20.')
    @click.option('--collect', default=60, help='Quantity of collects, default is 60.')
    @click.option('--comment', default=150, help='Quantity of comments, default is 150.')
    def forge(user, follow, share, tag, collect, comment):
        """Generate fake data."""
        from WeShare.fakes import fake_admin, fake_share, fake_follow, fake_tag, \
            fake_user, fake_collect, fake_comment

        db.drop_all()
        db.create_all()

        click.echo('Initializing the roles and permissions...')
        Role.init_role()
        click.echo('Generating the administrator...')
        fake_admin()
        click.echo('Generating %d users...' % user)
        fake_user(user)
        click.echo('Generating %d follows...' % follow)
        fake_follow(follow)
        click.echo('Generating %d tags...' % tag)
        fake_tag(tag)
        click.echo('Generating %d shares...' % share)
        fake_share(share)
        click.echo('Generating %d collects...' % share)
        fake_collect(collect)
        click.echo('Generating %d comments...' % comment)
        fake_comment(comment)
        click.echo('Done.')