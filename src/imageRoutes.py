from flask import Flask, jsonify, make_response,abort, request, render_template, Blueprint,redirect,url_for
from common import is_authenticated,error,create_thumbnail
import db
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import base64
import os


ImageRoutes = Blueprint('Image_Routes', __name__,
						template_folder='templates')

@ImageRoutes.route('/api/v1.0/uploadImage',methods=['POST'])
@is_authenticated()
def upload_image(newToken):
	
	file = request.files['file']
	image_buffer = create_thumbnail(file)

	username = request.cookies.get('username')
	
	S3_BUCKET = os.environ.get('S3_BUCKET_NAME')

	user = db.session.query(db.Users).filter_by(username=username).first()

	db.session.begin()

	newImage = db.Images(user_id=user.id)
	db.session.add(newImage)
	db.session.flush()
	shortenedName = base64.b64encode(str(newImage.id))
	newImage.src = shortenedName

	db.session.commit()

	
	conn = S3Connection()
	file.seek(0,0)
	bucket = conn.get_bucket(S3_BUCKET)
	k = bucket.new_key(shortenedName)
	k.set_contents_from_file(file)
	k.set_acl('public-read')


	k = bucket.new_key(shortenedName+".thumbnail")
	k.set_contents_from_string(image_buffer.getvalue())
	k.set_acl('public-read')

	resp = make_response('/imagography',200)
	resp.set_cookie('token',newToken)

	return resp


@ImageRoutes.route('/api/v1.0/<imageSrc>')
def view_image(imageSrc):
	image = db.session.query(db.Images).filter_by(src=imageSrc).first()
	if image is None:
		return 'Image not found',404

	return make_response(render_template('imageView.html',src=imageSrc,static_host=os.getenv('S3_STATIC_SITE')),200)

