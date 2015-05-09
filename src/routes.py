import db
import os,binascii
from flask import Flask, jsonify, make_response,abort, request, render_template, Blueprint
from passlib.hash import pbkdf2_sha256
from flask.ext.cors import CORS
import os.path
from userRoutes import UserRoutes
from functools import update_wrapper

app = Flask(__name__)
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
	authenticated = false

	if token is not None and user is not None:
		if db.session.query(db.Users).filter_by(username = user,token = token).first() is not None:
			authenticated = true

	return authenticated
		

def is_authenticated():
	def decorator(fn):
		def wrapped_function(*args, **kwargs):
			# First check if user is authenticated.
			if not logged_in():
				return redirect(url_for('login'))
			# For authorization error it is better to return status code 403
			# and handle it in errorhandler separately, because the user could
			# be already authenticated, but lack the privileges.
			return fn(*args, **kwargs)
		return update_wrapper(wrapped_function, fn)
	return decorator

@app.errorhandler(403)
def forbidden_403(exception):
	return 'Authentication Error', 403

@is_authenticated()
@app.route('/')
def index():
	return make_response(render_template('login.html',hosturl=os.getenv('API_HOST','http://localhost:5001')),200)


if __name__ == '__main__':
		app.run(debug=True,host='0.0.0.0',port=int(os.getenv("PORT","6001")))