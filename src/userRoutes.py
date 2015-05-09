import db
import os,binascii
from flask import Flask, jsonify, make_response,abort, request, render_template, Blueprint
from passlib.hash import pbkdf2_sha256
from functools import update_wrapper
from flask.ext.cors import CORS
import os.path


UserRoutes = Blueprint('User_Routes', __name__,
                        template_folder='templates')

@UserRoutes.route('/api/v1.0/user/adduser', methods=['POST'])
def new_user():
	username = request.json.get('username')
	password = request.json.get('password')
	email = request.json.get('email')
	first_name = request.json.get('firstname')
	last_name = request.json.get('lastname')

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

	return make_response(render_template('login.html',hosturl=os.getenv('API_HOST','http://localhost:5001'),successful="true"),200)

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

	if persistLogin is not None:
		resp = make_response(render_template('some.html', 200))
		db.session.begin()
		user.token =  binascii.b2a_hex(os.urandom(15))
		db.session.commit()
		resp.set_cookie('token',user.token)
		resp.set_cookie('username',username)
		return resp


	return make_response(('imagography.html'),200)

##############################################################################################