#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Zhihao
@File:      admin.py
@Time:      2021/02/18
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/index')
def index():
    return ""