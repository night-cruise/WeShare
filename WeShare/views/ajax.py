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
from flask import Blueprint

ajax_bp = Blueprint('ajax', __name__)

@ajax_bp.route('/notifications-count')
def notifications_count():
    return ""