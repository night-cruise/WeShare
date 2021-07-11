#!/user/bin/python
# -*-coding:UTF-8-*-
""" 
@Author:    Night Cruising
@File:      user.py
@Time:      2021/02/25
@Version:   3.7.3
@Desc:      None
"""
from flask_login import current_user
# here put the import lib
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields import StringField, TextAreaField, SubmitField, HiddenField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Regexp, Optional, Email, EqualTo
from wtforms.validators import ValidationError

from WeShare.models import User


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    username = StringField('Username', validators=[DataRequired(), Length(1, 20),
                                                   Regexp(r'^[a-zA-Z0-9]*$',
                                                          message='The username should contain only a-z, A-Z and 0-9.')
                                                   ])
    location = StringField('City', validators=[Optional(), Length(0, 50)])
    website = StringField('Website', validators=[Optional(), Length(0, 255)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(0, 120)])
    submit = SubmitField()

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class UploadAvatarForm(FlaskForm):
    image = FileField('Upload', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], 'The file format should be .jpg or .png.')
    ])
    submit = SubmitField()


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('Crop and Update')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 254), Email()])
    submit = SubmitField()

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('The email is already in use.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField()


class NotificationSettingForm(FlaskForm):
    receive_comment_notification = BooleanField('New comment')
    receive_follow_notification = BooleanField('New follower')
    receive_collect_notification = BooleanField('New collector')
    submit = SubmitField()


class PrivacySettingForm(FlaskForm):
    public_collections = BooleanField('Public my collection')
    submit = SubmitField()


class DeleteAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    submit = SubmitField()

    def validate_username(self, field):
        if field.data != current_user.username:
            raise ValidationError('Wrong username.')
