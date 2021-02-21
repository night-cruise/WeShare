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
from flask import Blueprint, request, current_app, url_for, send_from_directory
from ..helpers import allowed_file
from flask_ckeditor import upload_fail, upload_success

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/index')
def index():
    return "<body></body>"

@main_bp.route('/explore')
def explore():
    return ""

@main_bp.route('/search')
def search():
    return ""

@main_bp.route('/show-notifications')
def show_notifications():
    return ""

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
    f.save(os.path.join(current_app.config['WESHARE_UPLOAD_PATH']), f.filename)
    url = url_for('.get_image', filename=f.filename)
    return upload_success(url, f.filename)
