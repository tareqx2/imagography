from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session, relationship, load_only
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import func, select
from sqlalchemy.dialects.postgresql import JSON
import os
Base = declarative_base()

engine = create_engine(os.getenv("DATABASE_URL",""))

class Users(Base):
	__tablename__ = 'users'
	id = Column(Integer,primary_key=True)
	username = Column(String(32))
	password = Column(Text)
	first_name = Column(Text)
	last_name = Column(Text)
	email = Column(Text)
	token = Column(Text)
	forgot_password_token = Column(Text)
	forgot_password_expiration = Column(DateTime, default=func.now())

	@property
	def serialize(self):
		return {
			'id' : self.id,
			'username': self.username,
			'password': self.password,
			'first_name': self.first_name,
			'last_name': self.last_name,
			'email': self.email
		}

class Images(Base):
	__tablename__ = 'images'
	id = Column(Integer,primary_key=True)
	user_id = Column(Integer,ForeignKey(Users.id))
	src = Column(Text)
	caption = Column(Text)
	thumbs_up = Column(Integer)

class Comments(Base):
	__tablename__ = 'comments'
	id = Column(Integer,primary_key=True)
	image_id = Column(Integer,ForeignKey(Images.id))
	user_id = Column(Integer,ForeignKey(Users.id))
	comment = Column(Text)


Base.metadata.create_all(engine)
session =  create_session(bind = engine)

Images.query.delete()
