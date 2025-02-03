from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship

class UserRoles:
    pass

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key= True, index=True)
    username = Column(String,unique=True )
    email = Column(String,unique=True )
    hashed_password = Column(String)
    role = Column(String)

    profile = relationship("Profiles", back_populates="user", uselist=False)


class Profiles(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    surname = Column(String)
    date_of_birth = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_verified = Column(Boolean)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates="profile", uselist=False)