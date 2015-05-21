import db
import os,binascii
from flask import Flask, jsonify, make_response,abort, request, render_template, Blueprint,url_for,redirect
from passlib.hash import pbkdf2_sha256
from flask.ext.cors import CORS
import os.path
from userRoutes import UserRoutes
from imageRoutes import ImageRoutes
from datetime import timedelta
from common import is_authenticated,error

app = Flask(__name__)
app.config["SESSION_COOKIE_SECURE"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10)
app.register_blueprint(UserRoutes)
app.register_blueprint(ImageRoutes)
cors = CORS(app)
#app.static_url_path = os.path.abspath(os.path.join(app.root_path, os.pardir))

##############################################################################################


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


if __name__ == '__main__':
		app.run(debug=True,host='0.0.0.0',port=int(os.getenv("PORT","6001")))