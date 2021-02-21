#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Zhihao
@File:      user.py
@Time:      2021/02/18
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
from flask import Blueprint

user_bp = Blueprint('user', __name__)

@user_bp.route('/index/<username>')
def index(username):
    return ""

@user_bp.route('/edit-profile')
def edit_profile():
    return ""