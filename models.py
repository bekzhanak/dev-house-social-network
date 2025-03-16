from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum, PrimaryKeyConstraint
from datetime import datetime
from sqlalchemy.orm import relationship
import enum

class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key= True, index=True)
    username = Column(String,unique=True )
    email = Column(String,unique=True )
    hashed_password = Column(String)
    role = Column(
        Enum(RoleEnum, name="role_enum"),
        nullable=False,
        server_default=RoleEnum.USER.value
    )

    profile = relationship("Profiles", back_populates="user", uselist=False)
    posts = relationship("Posts", back_populates="user")
    comments = relationship("Comments", back_populates="user")
    likes = relationship("Likes", back_populates="user")
    emails = relationship("Emails", back_populates="user")

    followers = relationship(
        'Followers',
        foreign_keys='Followers.following_id',
        back_populates='following_user',
        cascade='all, delete-orphan'
    )

    following = relationship(
        'Followers',
        foreign_keys='Followers.follower_id',
        back_populates='follower_user',
        cascade='all, delete-orphan'
    )


class Profiles(Base):
    __tablename__ = 'profiles'
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    surname = Column(String)
    date_of_birth = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates="profile", uselist=False)


class Posts(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key = True, index = True)
    title = Column(Text)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates="posts")
    comments = relationship("Comments", back_populates="posts")
    likes = relationship("Likes", back_populates="posts")


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key = True, index = True)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    user = relationship("Users", back_populates="comments")
    posts = relationship("Posts", back_populates="comments")


class Likes(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key = True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    user = relationship("Users", back_populates="likes")
    posts = relationship("Posts", back_populates="likes")

class Followers(Base):
    __tablename__ = 'followers'

    follower_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    following_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        PrimaryKeyConstraint('follower_id', 'following_id'),
    )

    follower_user = relationship(
        'Users',
        foreign_keys=[follower_id],
        back_populates='following'
    )

    following_user = relationship(
        'Users',
        foreign_keys=[following_id],
        back_populates='followers'
    )

class Emails(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key = True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    verification_code = Column(Integer)
    attempts = Column(Integer, default=0)

    user = relationship("Users", back_populates="emails")
