from functools import update_wrapper
from flask import Flask, jsonify, make_response,abort, request, render_template, Blueprint,url_for,redirect
from passlib.hash import pbkdf2_sha256
from datetime import timedelta
import db
import os,binascii
from PIL import Image
from StringIO import StringIO

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

def create_thumbnail(image):
	size = 210,210
	im = Image.open(image)
	im.thumbnail(size,Image.ANTIALIAS)

	return serve_pil_image(im)

def serve_pil_image(pil_img):
    img_io = StringIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return img_io