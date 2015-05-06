import db
import os,binascii
from flask import Flask, jsonify, make_response,abort, request, render_template, Blueprint
from passlib.hash import pbkdf2_sha256
from flask.ext.cors import CORS
import os.path
from userRoutes import UserRoutes

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


@app.route('/')
def index():
	return make_response(render_template('login.html'),200)


if __name__ == '__main__':
		app.run(debug=True,host='0.0.0.0',port=int(os.getenv("PORT","5001")))