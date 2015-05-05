from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session, relationship, load_only
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import func, select

Base = declarative_base()

engine = create_engine("sqlite:///imagography.db")

class Users(Base):
	__tablename__ = 'users'
	id = Column(Integer,primary_key=True)
	username = Column(String(32))
	password = Column(Text)

	@property
	def serialize(self):
		return {
			'id' : self.id,
			'username': self.username,
			'password': self.password
		}

Base.metadata.create_all(engine)
session =  create_session(bind = engine)
