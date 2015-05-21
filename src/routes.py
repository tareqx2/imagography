import db
import os,binascii
from flask import Flask, jsonify, make_response,abort, request, render_template, Blueprint,url_for,redirect
from passlib.hash import pbkdf2_sha256
from flask.ext.cors import CORS
import os.path
from userRoutes import UserRoutes
from functools import update_wrapper
from datetime import timedelta
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key

app = Flask(__name__)
app.config["SESSION_COOKIE_SECURE"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10)
app.register_blueprint(UserRoutes)
cors = CORS(app)
#app.static_url_path = os.path.abspath(os.path.join(app.root_path, os.pardir))

##############################################################################################


def error(status_code, app_code,message, action = ""):
	response = jsonify({
		'status': status_code,
		'appCode': app_code,
		'message': message,
		'action': action
	})
	response.status_code = status_code
	return response

def logged_in():
	token = request.cookies.get('token')
	user = request.cookies.get('username')
	authenticated = False

	if token is not None and user is not None:
		if db.session.query(db.Users).filter_by(username = user,token = token).first() is not None:
			authenticated = True

	return authenticated
		

def is_authenticated():
	def decorator(fn):
		def wrapped_function(*args, **kwargs):
			# First check if user is authenticated.
			if not logged_in():
				return make_response(render_template('login.html',session='expired'),200)

			#we want to generate a new token for the user
			token = request.cookies.get('token')
			username = request.cookies.get('username')
			db.session.begin()
			newToken = binascii.b2a_hex(os.urandom(15))
			user = db.session.query(db.Users).filter_by(username= username).first()
			user.token = newToken

			db.session.commit()
			# For authorization error it is better to return status code 403
			# and handle it in errorhandler separately, because the user could
			# be already authenticated, but lack the privileges.
			args = [newToken]
			return fn(*args, **kwargs)
		return update_wrapper(wrapped_function, fn)
	return decorator

@app.errorhandler(403)
def forbidden_403(exception):
	return 'Authentication Error', 403

@app.route('/')
def index():
	token = request.cookies.get('token')
	username = request.cookies.get('username')
	if token is not None and username is not None:
		return redirect('imagography')

	successful = request.args.get('successful')
	messageSent = request.args.get('messageSent')
	passwordChanged = request.args.get('passwordChanged')

	return make_response(render_template('login.html',successful=successful,messageSent=messageSent,passwordChanged=passwordChanged,hosturl=os.getenv('API_HOST','http://localhost:5001')),200)

@app.route('/imagography')
@is_authenticated()
def landing_page(newToken):

	username = request.cookies.get('username')
	images = db.session.query(db.Images).all()

	resp = make_response(render_template('imagography.html',images = images,hosturl=os.getenv('API_HOST','http://localhost:5001'),static_host=os.getenv('S3_STATIC_SITE','http://localhost:5001')),200)
	resp.set_cookie('token',newToken)

	return resp


@app.route('/api/v1.0/uploadImage',methods=['POST'])
@is_authenticated()
def upload_image(newToken):
	
	file = request.files['file']

	username = request.cookies.get('username')
	
	S3_BUCKET = os.environ.get('S3_BUCKET_NAME')

	conn = S3Connection()

	bucket = conn.get_bucket(S3_BUCKET)
	k = bucket.new_key(file.filename+"."+username)
	k.set_contents_from_file(file)
	k.set_acl('public-read')

	user = db.session.query(db.Users).filter_by(username=username).first()

	db.session.begin()

	newImage = db.Images(user_id=user.id,src=file.filename+"."+username)

	db.session.add(newImage)
	db.session.commit()

	resp = make_response('/imagography',200)
	resp.set_cookie('token',newToken)

	return resp


if __name__ == '__main__':
		app.run(debug=True,host='0.0.0.0',port=int(os.getenv("PORT","6001")))