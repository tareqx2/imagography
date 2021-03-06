import db
import os,binascii
from flask import Flask, jsonify, make_response,abort, request, render_template, Blueprint,redirect,url_for
from passlib.hash import pbkdf2_sha256
from functools import update_wrapper
from flask.ext.cors import CORS
import os.path
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from common import is_authenticated,error

UserRoutes = Blueprint('User_Routes', __name__,
						template_folder='templates')

@UserRoutes.route('/api/v1.0/user/adduser', methods=['POST'])
def new_user():
	username = request.json.get('username')
	password = request.json.get('password')
	email = request.json.get('email')
	first_name = request.json.get('fname')
	last_name = request.json.get('lname')

	if not username or not password or not email:
		return error(400, 1010,'Some login information was not provided')
	hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

	if db.session.query(db.Users).filter_by(username = username).first() is not None:
		return error(400, 1020,'This username is not available') # existing user
	if db.session.query(db.Users).filter_by(email = email).first() is not None:
		return error(400, 1040,'A user with this email already exists') # existing user
	user = db.Users(username = username)
	user.password = hash
	user.email = email
	user.first_name = first_name
	user.last_name = last_name
	db.session.begin()
	db.session.add(user)
	db.session.commit()

	return jsonify({'redirectUrl':'/',"params":"successful=true"})

##############################################################################################

@UserRoutes.route('/api/v1.0/user/login', methods=['POST'])
def login_user():
	username = request.json.get('username')
	password = request.json.get('password')

	user = db.session.query(db.Users).filter_by(username= username).first()
	if user is None:
		return error(400, 1030, "Incorrect username or password") # user does not exist
	successfulLogin = pbkdf2_sha256.verify(password, user.password)
	if not successfulLogin:
		return error(400,1030, 'Incorrect username or password') #incorrect password

	resp = make_response(jsonify({'redirectUrl':'/imagography'}),200)

	db.session.begin()
	user.token =  binascii.b2a_hex(os.urandom(15))
	db.session.commit()
	resp.set_cookie('token',user.token)
	resp.set_cookie('username',username)

	return resp

##############################################################################################
@UserRoutes.route('/api/v1.0/user/resetPassword',methods=['POST'])
def resetPassword():
	new_password = request.json.get('new_password')
	resetToken = request.cookies.get('resetToken')

	user = db.session.query(db.Users).filter_by(forgot_password_token=resetToken).first()

	if not user:
		return error(400, 1090,'An error has occured, please try again later')
	if datetime.datetime.utcnow() > user.forgot_password_expiration:
		return error(400,1070,'Forgotten email token has expired, please try again')

	db.session.begin()
	user.password = pbkdf2_sha256.encrypt(new_password, rounds=200000, salt_size=16)
	user.forgot_password_expiration = datetime.datetime.utcnow()
	db.session.commit()

	return jsonify({'redirectUrl':'/',"params":"passwordChanged=true"}),200

##############################################################################################
@UserRoutes.route('/api/v1.0/user/passwordReset/<resetToken>',methods=['GET'])
def reset_password(resetToken):

	user = db.session.query(db.Users).filter_by(forgot_password_token=resetToken).first()
	if not user:
		return error(400, 1080,'Issue with forgotten email token')
	if datetime.datetime.utcnow() > user.forgot_password_expiration:
		return error(400,1070,'Forgotten email token has expired, please try again')

	response = make_response(render_template('login.html',resetPassword='true'),200)
	response.set_cookie('resetToken',resetToken)

	return response

##############################################################################################
@UserRoutes.route('/api/v1.0/user/forgotPassword',methods=['POST'])
def forgot_password():
	email = request.json.get('email')

	user = db.session.query(db.Users).filter_by(email=email).first()
	if not user:
		return error(400, 1050, 'no user with that email')

	me="admin@imagography.com"
	recipient=email

	msg = MIMEMultipart('alternative')

	msg['Subject'] = "Password reset for imagography"
	msg['From'] = me
	msg['To'] = recipient
	forgotToken = binascii.b2a_hex(os.urandom(15))
	html = "To reset your password simply follow this link: "+ os.getenv('API_HOST','http://localhost:5001') + "/api/v1.0/user/passwordReset/" + forgotToken
	msg.attach(MIMEText(html, 'html'))

	smtp = smtplib.SMTP(os.getenv('MAILGUN_SMTP_SERVER',''),os.getenv('MAILGUN_SMTP_PORT',''))
	smtp.login(os.getenv('MAILGUN_SMTP_LOGIN',''),os.getenv('MAILGUN_SMTP_PASSWORD',''))
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	smtp.sendmail(me, recipient, msg.as_string())
	smtp.quit()


	db.session.begin()
	user.forgot_password_token = forgotToken
	user.forgot_password_expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=20)
	db.session.commit()

	return jsonify({'redirectUrl':'/',"params":"messageSent=true"}),200


