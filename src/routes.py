import db
import os
from flask import Flask, jsonify
from flask import abort
from flask import request
from passlib.hash import pbkdf2_sha256
 
app = Flask(__name__)

##############################################################################################

@app.route('/api/v1.0/user/adduser', methods=['POST'])
def new_user():

	username = request.json.get('username')
	password = request.json.get('password')
	hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
	print hash
	if username is None or password is None:
		abort(400) # missing arguments
	if db.session.query(db.Users).filter_by(username = username).first() is not None:
		abort(400) # existing user
	user = db.Users(username = username)
	user.password = hash
	db.session.begin()
	db.session.add(user)
	db.session.commit()

	return jsonify({ 'username': user.username }), 201

##############################################################################################

@app.route('/api/v1.0/user/login', methods=['POST'])
def login_user():
	username = request.json.get('username')
	password = request.json.get('password')
	hash = db.session.query(db.Users).filter_by(username= username).first()
	if hash is None:
		abort(400) # user does not exist
	successfulLogin = pbkdf2_sha256.verify(password, hash.password)
	if not successfulLogin:
		abort(400) #incorrect password
	return jsonify({'username':username}),200

##############################################################################################

if __name__ == '__main__':
		app.run(host='0.0.0.0',port=int(os.getenv("PORT","5001")))