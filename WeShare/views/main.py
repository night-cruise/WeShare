#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Zhihao
@File:      main.py
@Time:      2021/02/18
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
import os
from flask import Blueprint, request, current_app, url_for, send_from_directory, render_template, flash, abort, redirect
from flask_login import login_required, current_user
from flask_ckeditor import upload_fail, upload_success, random_filename

from WeShare.helpers import allowed_file, redirect_back, flash_errors
from WeShare.extensions import db
from WeShare.models import Share, Follow, Tag, User, Notification, Comment, Collect
from WeShare.forms.main import CommentForm, TagForm, ShareForm, EditShareForm
from WeShare.decorators import confirm_required, permission_required
from WeShare.notifications import push_collect_notification, push_comment_notification

from sqlalchemy.sql.expression import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/index')
def index():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['WESHARE_SHARE_PER_PAGE']
        pagination = Share.query \
            .join(Follow, Follow.followed_id==Share.author_id) \
            .filter(Follow.follower_id==current_user.id) \
            .order_by(Share.timestamp.desc()) \
            .paginate(page, per_page)
        shares = pagination.items
    else:
        pagination = None
        shares = None
    tags = Tag.query.join(Tag.shares).group_by(Tag.id).order_by(func.count(Share.id).desc()).limit(10)
    return render_template('main/index.html', shares=shares, pagination=pagination, tags=tags)

@main_bp.route('/explore')
def explore():
    shares = Share.query.order_by(func.random()).limit(12)
    return render_template('main/explore.html', shares=shares)

@main_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if q == '':
        flash('Enter keyword about share, user or tag.', 'warning')
        return redirect_back()

    category = request.args.get('category', 'share')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['WESHARE_SEARCH_RESULT_PER_PAGE']
    if category == 'user':
        pagination = User.query.whooshee_search(q).paginate(page, per_page)
    elif category == 'tag':
        pagination = Tag.query.whooshee_search(q).paginate(page, per_page)
    else:
        pagination = Share.query.whooshee_search(q).paginate(page, per_page)
    results = pagination.items
    return render_template('main/search.html', q=q, results=results, pagination=pagination, category=category)


@main_bp.route('/notifications')
@login_required
def show_notifications():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['WESHARE_NOTIFICATION_PER_PAGE']
    notifications = Notification.query.with_parent(current_user)
    filter_rule = request.args.get('filter')
    if filter_rule == 'unread':
        notifications = notifications.filter_by(is_read=False)
    pagination = notifications.order_by(Notification.timestamp.desc()).paginate(page, per_page)
    notifications = pagination.items
    return render_template('main/notifications.html', pagination=pagination, notifications=notifications)

@main_bp.route('/notifications/read/all', methods=['POST'])
@login_required
def read_all_notification():
    for notification in current_user.notifications:
        notification.is_read = True
    db.session.commit()
    flash('All notifications archived.', 'success')
    return redirect(url_for('.show_notifications'))

@main_bp.route('/notification/read/<int:notification_id>', methods=['POST'])
@login_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if current_user != notification.receiver:
        abort(403)

    notification.is_read = True
    db.session.commit()
    flash('Notification archived.', 'success')
    return redirect(url_for('.show_notifications'))

@main_bp.route('/new/share', methods=['GET', 'POST'])
@login_required
@confirm_required
@permission_required('SHARE')
def new_share():
    form = ShareForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        share = Share(
            title = title,
            body = body,
            author = current_user._get_current_object()
        )
        for name in form.tag.data.split():
            tag = Tag.query.filter_by(name=name).first()
            if tag is None:
                tag = Tag(name=name)
                db.session.add(tag)
            if tag not in share.tags:
                share.tags.append(tag)
        db.session.add(share)
        db.session.commit()
        flash('Share success.', 'info')
        return redirect(url_for('main.show_share', share_id=share.id))
    return render_template('main/new_share.html', form=form)

@main_bp.route('/share/<int:share_id>')
def show_share(share_id):
    share = Share.query.get_or_404(share_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['WESHARE_COMMET_PER_PAGE']
    pagination = Comment.query.with_parent(share).order_by(Comment.timestamp.asc()).paginate(page, per_page)
    comments = pagination.items

    comment_form = CommentForm()
    tag_form = TagForm()
    return render_template('main/share.html', share=share, comment_form=comment_form, tag_form=tag_form,
                           pagination=pagination, comments=comments
                           )

@main_bp.route('/share/n/<int:share_id>')
def share_next(share_id):
    share = Share.query.get_or_404(share_id)
    share_p = Share.query.with_parent(share.author).filter(Share.id > share_id).order_by(Share.id.asc()).first()

    if share_p is None:
        flash('This is already the first one.', 'info')
        return redirect(url_for('.show_share', share_id=share.id))
    return redirect(url_for('.show_share', share_id=share_p.id))

@main_bp.route('/share/p/<int:share_id>')
def share_previous(share_id):
    share = Share.query.get_or_404(share_id)
    share_n = Share.query.with_parent(share.author).filter(Share.id < share_id).order_by(Share.id.desc()).first()

    if share_n is None:
        flash('This is already the last one.', 'info')
        return redirect(url_for('.show_share', share_id=share.id))
    return redirect(url_for('.show_share', share_id=share_n.id))

@main_bp.route('/edit/share/<int:share_id>', methods=['GET', 'POST'])
@login_required
def edit_share(share_id):
    share = Share.query.get_or_404(share_id)
    if current_user != share.author and not current_user.can('MODERATE'):
        abort(403)
    form = EditShareForm()
    if form.validate_on_submit():
        share.title = form.title.data
        share.body = form.body.data
        db.session.commit()
        flash('Edit success.', 'info')
        return redirect(url_for('main.show_share', share_id=share.id))
    form.title.data = share.title
    form.body.data = share.body
    return render_template('main/edit_share.html', form=form)

@main_bp.route('/delete/share/<int:share_id>', methods=['POST'])
@login_required
def delete_share(share_id):
    share = Share.query.get_or_404(share_id)
    if current_user != share.author and not current_user.can('MODERATE'):
        abort(403)

    db.session.delete(share)
    db.session.commit()
    flash('Share deleted.', 'info')

    share_n = Share.query.with_parent(share.author).filter(Share.id < share_id).order_by(Share.timestamp.desc()).first()
    if share_n is None:
        share_p = Share.query.with_parent(share.author).filter(Share.id > share_id).order_by(Share.timestamp.asc()).first()
        if share_p is None:
            return redirect(url_for('user.index', username=share.author.username))
        return redirect(url_for('.show_share', share_id=share_p.id))
    return redirect(url_for('.show_share', share_id=share_n.id))

@main_bp.route('/collect/<int:share_id>', methods=['POST'])
@login_required
@confirm_required
@permission_required('COLLECT')
def collect(share_id):
    share = Share.query.get_or_404(share_id)
    if current_user.is_collecting(share):
        flash('Alread collected.', 'info')
        return redirect(url_for('.show_share', share_id=share_id))
    current_user.collect(share)
    flash('Share collected.', 'success')
    if current_user !=  share.author and share.author.receive_collect_notification:
        push_collect_notification(current_user, share_id, share.author)
    return redirect(url_for('.show_share', share_id=share_id))

@main_bp.route('/uncollect/<int:share_id>', methods=['POST'])
@login_required
def uncollect(share_id):
    share = Share.query.get_or_404(share_id)
    if not current_user.is_collecting(share):
        flash('Not collect yet.', 'info')
        return redirect(url_for('.show_share', share_id=share_id))

    current_user.uncollect(share)
    flash('Share uncollected.', 'info')
    return redirect(url_for('.show_share', share_id=share_id))

@main_bp.route('/share/<int:share_id>/collectors')
def show_collectors(share_id):
    share = Share.query.get_or_404(share_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['WESHARE_USER_PER_PAGE']
    pagination = Collect.query.with_parent(share).order_by(Collect.timestamp.desc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('main/collectors.html', collects=collects, pagination=pagination, share=share)

@main_bp.route('/report/share/<int:share_id>', methods=['POST'])
@login_required
def report_share(share_id):
    share = Share.query.get_or_404(share_id)
    share.flag += 2
    db.session.commit()
    flash('Share reported.', 'success')
    return redirect(url_for('.show_share', share_id=share_id))

@main_bp.route('/share/<int:share_id>/new/comment', methods=['GET', 'POST'])
@login_required
@permission_required('COMMENT')
def new_comment(share_id):
    share = Share.query.get_or_404(share_id)
    page = request.args.get('page', 1, type=int)
    form = CommentForm()
    if form.validate_on_submit():
        body = form.body.data
        author = current_user._get_current_object()
        comment = Comment(body=body, author=author, share=share)

        replied_id = request.args.get('reply')
        if replied_id:
            comment.replied = Comment.query.get_or_404(replied_id)
            if comment.replied.author.receive_comment_notification:
                push_comment_notification(share_id=share_id, receiver=comment.replied.author, page=page)

        db.session.add(comment)
        db.session.commit()
        flash('Comment published.', 'success')

        if current_user != share.author and share.author.receive_comment_notification:
            push_comment_notification(share_id, receiver=share.author, page=page)

        flash_errors(form)
        return redirect(url_for('.show_share', share_id=share_id, page=page))

@main_bp.route('/set-comment/<int:share_id>', methods=['POST'])
@login_required
def set_comment(share_id):
    share = Share.query.get_or_404(share_id)
    if current_user != share.author and not current_user.can('MODERATE'):
        abort(403)
    if share.can_comment:
        share.can_comment = False
        flash('Comment disabled.', 'info')
    else:
        share.can_comment = True
        flash('Comment enabled.', 'info')
    db.session.commit()
    return redirect(url_for('.show_share', share_id=share_id))

@main_bp.route('/reply/comment/<int:comment_id>')
@login_required
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(
        url_for(
            '.show_share', share_id=comment.share_id,
            reply=comment_id, author=comment.author.name
        ) + '#comment-form'
    )

@main_bp.route('/delete/comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user != comment.author and current_user != comment.share.author \
            and not current_user.can('MODERATE'):
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'info')
    return redirect(url_for('.show_share', share_id=comment.share_id))

@main_bp.route('/report/comment/<int:comment_id>', methods=['POST'])
@login_required
def report_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.flag += 1
    db.session.commit()
    flash('Comment reported.', 'success')
    return redirect(url_for('.show_share', share_id=comment.share_id))

@main_bp.route('/share/<int:share_id>/new/tag', methods=['POST'])
def new_tag(share_id):
    share = Share.query.get_or_404(share_id)
    if current_user != share.author and not current_user.can('MODERATE'):
        abort(403)

    form = TagForm()
    if form.validate_on_submit():
        for name in form.tag.data.split():
            tag = Tag.query.filter_by(name=name).first()
            if tag is None:
                tag = Tag(name=name)
                db.session.add(tag)
            if tag not in share.tags:
                share.tags.append(tag)
        db.session.commit()
        flash('Tag added.', 'success')
    flash_errors(form)
    return redirect(url_for('.show_share', share_id=share_id))

@main_bp.route('/tag/<int:tag_id>', defaults={'order': 'by_time'})
@main_bp.route('/tag/<int:tag_id>/<order>')
def show_tag(tag_id, order):
    tag = Tag.query.get_or_404(tag_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['WESHARE_SHARE_PER_PAGE']
    order_rule = 'time'
    pagination = Share.query.with_parent(tag).order_by(Share.timestamp.desc()).paginate(page, per_page)
    shares = pagination.items

    if order == 'by_collects':
        shares.sort(key=lambda x: len(x.collectors), reverse=True)
        order_rule = 'collects'
    return render_template('main/tag.html', tag=tag, pagination=pagination, shares=shares, order_rule=order_rule)


@main_bp.route('/delete/tag/<int:share_id>/<int:tag_id>', methods=["POST"])
@login_required
def delete_tag(share_id, tag_id):
    tag = Tag.query.get_or_404(tag_id)
    share = Share.query.get_or_404(share_id)
    if current_user != share.author and not current_user.can('MODERATE'):
        abort(403)

    share.tags.remove(tag)
    db.session.commit()
    if not tag.shares:
        db.session.delete(tag)
        db.session.commit()
    flash('Tag deleted.', 'info')
    return redirect(url_for('.show_share', share_id=share_id))

@main_bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)

@main_bp.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['WESHARE_UPLOAD_PATH'], filename)

@main_bp.route('/upload', methods=['POST'])
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('Image only!')
    filename = random_filename(f.filename)
    f.save(os.path.join(current_app.config['WESHARE_UPLOAD_PATH'], filename))
    url = url_for('.get_image', filename=filename)
    return upload_success(url, filename)
