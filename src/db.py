from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session, relationship, load_only
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import func, select
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()

engine = create_engine("postgres://onqgylvwetfmrs:msoX2pm2aumNGhPVmNMMowV6LI@ec2-23-23-81-221.compute-1.amazonaws.com:5432/d25efctra7hv7m")

class Users(Base):
	__tablename__ = 'users'
	id = Column(Integer,primary_key=True)
	username = Column(String(32))
	password = Column(Text)
	first_name = Column(Text)
	last_name = Column(Text)
	email = Column(Text)
	token = Column(Text)

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

Base.metadata.create_all(engine)
session =  create_session(bind = engine)
