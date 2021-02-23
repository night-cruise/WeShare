#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Night Cruising
@File:      main.py
@Time:      2021/02/22
@Version:   3.7.3
@Desc:      None
"""
# here put the import lib
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField()

class TagForm(FlaskForm):
    tag = StringField('Add Tag (use space to separate)', validators=[Optional(), Length(0, 64)])
    submit = SubmitField()

class ShareForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 64)])
    tag = StringField('Add Tag (user space to separate)', validators=[Optional()])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()

class EditShareForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 64)])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()