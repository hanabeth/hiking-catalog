import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(50))
	email = Column(String(50))

class Location(Base):
	__tablename__ = 'location'

	id = Column(Integer, primary_key=True)
	country = Column(String(25), nullable=False)
	trails = relationship('HikingTrail', cascade='delete')
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		return {
			'id': self.id,
			'country': self.country
		}


class HikingTrail(Base):
	__tablename__ = 'hiking_trail'

	id = Column(Integer, primary_key=True)
	trailName = Column(String(50))
	description = Column(String(500))
	website = Column(String(80))
	province = Column(String(25), nullable=False)
	park = Column(String(25), nullable=False)
	location_id = Column(Integer, ForeignKey('location.id'))
	location = relationship(Location)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

# Create decorator method - put data into format that Flask can use
	@property
	def serialize(self):
		return {
			'id': self.id,
			'trailName': self.trailName,
			'description': self.description,
			'province': self.province,
			'park': self.park,
			'website': self.website
		}



engine = create_engine('sqlite:///hiking.db')


Base.metadata.create_all(engine)
