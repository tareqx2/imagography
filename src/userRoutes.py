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

UserRoutes = Blueprint('User_Routes', __name__,
						template_folder='templates')

def error(status_code, app_code,message, action = ""):
	response = jsonify({
		'status': status_code,
		'appCode': app_code,
		'message': message,
		'action': action
	})
	response.status_code = status_code
	return response

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
		return error(400, 1020,'User already exists') # existing user
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
	persistLogin = request.json.get('persistLogin')

	user = db.session.query(db.Users).filter_by(username= username).first()
	if user is None:
		return error(400, 1030, "No user with that username found") # user does not exist
	successfulLogin = pbkdf2_sha256.verify(password, user.password)
	if not successfulLogin:
		return error(400,1040, 'Incorrect Password') #incorrect password

	resp = make_response(jsonify({'redirectUrl':'/imagography'}),200)

	db.session.begin()
	user.token =  binascii.b2a_hex(os.urandom(15))
	db.session.commit()
	resp.set_cookie('token',user.token)
	resp.set_cookie('username',username)

	return resp

##############################################################################################
@UserRoutes.route('/passwordReset/<resetToken>',methods=['GET'])
def reset_password():

	return 200

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



