#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Zhihao
@File:      ajax.py
@Time:      2021/02/18
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
from flask import Blueprint, jsonify, render_template
from flask_login import current_user

from WeShare.models import Notification, Share, User
from WeShare.notifications import push_collect_notification, push_follow_notification

ajax_bp = Blueprint('ajax', __name__)

@ajax_bp.route('/notifications-count')
def notifications_count():
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 403
    count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
    return jsonify(count=count)

@ajax_bp.route('/get-profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('main/profile_popup.html', user=user)

@ajax_bp.route('/collectors-count/<int:share_id>')
def collectors_count(share_id):
    share = Share.query.get_or_404(share_id)
    count = len(share.collectors)
    return jsonify(count=count)

@ajax_bp.route('/uncollec/<int:share_id>', methods=['POST'])
def uncollect(share_id):
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 403

    share = Share.query.get_or_404(share_id)
    if not current_user.is_collecting(share):
        return jsonify(message='Not collect yet.'), 400

    current_user.uncollect(share)
    return jsonify(message='Collect canceled.')

@ajax_bp.route('/collect/<int:share_id>', methods=['POST'])
def collect(share_id):
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 403
    if not current_user.confirmed:
        return jsonify(message='Confirm account required.'), 403
    if not current_user.can('COLLECT'):
        return jsonify(message='No permission.'), 403

    share = Share.query.get_or_404(share_id)
    if current_user.is_collecting(share):
        return jsonify(message='Already collected.'), 400

    current_user.collect(share)
    if current_user != share.author and share.author.receive_collect_notification:
        push_collect_notification(collector=current_user, share_id=share_id, receiver=share.author)
    return jsonify(message='Share collected.')

@ajax_bp.route('/followers-count/<int:user_id>')
def followers_count(user_id):
    user = User.query.get_or_404(user_id)
    count = user.followers.count() - 2
    return jsonify(count=count)

@ajax_bp.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 403

    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        return jsonify(message='Not follow yet.'), 400

    current_user.unfollow(user)
    return jsonify(message='Follow canceled.')

@ajax_bp.route('/follow/<username>', methods=['POST'])
def follow(username):
    if not current_user.is_authenticated:
        return jsonify(message='Login required.'), 403
    if not current_user.confirmed:
        return jsonify(message='Confirm account required.'), 400
    if not current_user.can('FOLLOW'):
        return jsonify(message='No permission.'), 403

    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        return jsonify(message='Already followed.'), 400

    current_user.follow(user)
    if user.receive_collect_notification:
        push_follow_notification(follower=current_user, receiver=user)
    return jsonify(message='User followed.')

