# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class City(Base):
  __tablename__ = 'city'

  # Columns
  id = Column(String(45), primary_key=True)
  name = Column(String(45), nullable=False)

  # Properties
  residents = relationship(
    'User', backref='location', primaryjoin='User.location_id==City.id'
  )
  natives = relationship(
    'User', backref='birthplace', primaryjoin='User.birthplace_id==City.id'
  )

  def __init__(self, id=None, name=None):
    self.id = id
    self.name = name

class Sex(Base):
  __tablename__ = 'sex'
  
  # Columns
  id = Column(CHAR(1), primary_key=True, autoincrement=False)

  # Properties
  users = relationship('User')

  def __init__(self, id=None):
    self.id = id

friendship = Table(
  'friendship', Base.metadata,
  Column('friend_a_id', String(45), ForeignKey('user.id'), primary_key=True),
  Column('friend_b_id', String(45), ForeignKey('user.id'), primary_key=True)
)

class User(Base):
  __tablename__ = 'user'

  # Columns
  id = Column(String(45), primary_key=True, autoincrement=False)
  name = Column(String(255), nullable=False)
  picture = Column(String(255))
  location_id = Column(String(45), ForeignKey('city.id'))
  birthplace_id = Column(String(45), ForeignKey('city.id'))
  sex = Column(CHAR(1), ForeignKey('sex.id'), nullable=False)
  birthdate = Column(Date)

  # Properties
  friends = relationship(
    'User', secondary=friendship, 
    primaryjoin=id==friendship.c.friend_a_id,
    secondaryjoin=id==friendship.c.friend_b_id
  )

  def __init__(self, id=None, name=None, location_id=None, picture=None, 
               birthplace_id=None, sex='?', birthdate=None):
    self.id = id
    self.name = name
    self.picture = picture
    self.location_id = location_id
    self.birthplace_id = birthplace_id
    self.sex = sex
    self.birthdate = birthdate

# This model of friendship was taken from:
# https://stackoverflow.com/questions/9116924/how-can-i-achieve-a-self-referencing-many-to-many-relationship-on-the-sqlalchemy
friendship_union = select([
  friendship.c.friend_a_id, 
  friendship.c.friend_b_id
]).union(
  select([
    friendship.c.friend_b_id, 
    friendship.c.friend_a_id
  ])
).alias()

User.all_friends = relationship(
  'User', secondary=friendship_union,
  primaryjoin=User.id==friendship_union.c.friend_a_id,
  secondaryjoin=User.id==friendship_union.c.friend_b_id,
  viewonly=True
)
