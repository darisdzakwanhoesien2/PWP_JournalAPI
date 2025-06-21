"""Module for ORM models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    """ORM model for a user."""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

    entries = relationship('Entry', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        """Return a string representation of the User."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    @classmethod
    def from_dict(cls, data):
        """Create a User instance from a dictionary."""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            registered_at=data.get('registered_at')
        )

    def to_dict(self):
        """Convert the User instance to a dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None
        }

class Entry(Base):
    """ORM model for an entry."""

    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='entries')
    comments = relationship('Comment', back_populates='entry', cascade='all, delete-orphan')
    edit_history = relationship('EditHistory', back_populates='entry', cascade='all, delete-orphan')

    def __repr__(self):
        """Return a string representation of the Entry."""
        return f"<Entry(id={self.id}, title='{self.title}', user_id={self.user_id})>"

    @classmethod
    def from_dict(cls, data):
        """Create an Entry instance from a dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            title=data.get('title'),
            content=data.get('content'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self):
        """Convert the Entry instance to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Comment(Base):
    """ORM model for a comment."""

    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('entries.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entry = relationship('Entry', back_populates='comments')
    user = relationship('User')

    def __repr__(self):
        """Return a string representation of the Comment."""
        return f"<Comment(id={self.id}, entry_id={self.entry_id}, user_id={self.user_id})>"

    @classmethod
    def from_dict(cls, data):
        """Create a Comment instance from a dictionary."""
        return cls(
            id=data.get('id'),
            entry_id=data.get('entry_id'),
            user_id=data.get('user_id'),
            content=data.get('content'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self):
        """Convert the Comment instance to a dictionary."""
        return {
            'id': self.id,
            'entry_id': self.entry_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EditHistory(Base):
    """ORM model for an edit history entry."""

    __tablename__ = 'edit_history'

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('entries.id', ondelete='CASCADE'), nullable=False)
    edited_at = Column(DateTime, default=datetime.utcnow)
    changes = Column(Text)  # JSON string or serialized changes

    entry = relationship('Entry', back_populates='edit_history')

    def __repr__(self):
        """Return a string representation of the EditHistory."""
        return f"<EditHistory(id={self.id}, entry_id={self.entry_id})>"

    @classmethod
    def from_dict(cls, data):
        """Create an EditHistory instance from a dictionary."""
        return cls(
            id=data.get('id'),
            entry_id=data.get('entry_id'),
            edited_at=data.get('edited_at'),
            changes=data.get('changes')
        )

    def to_dict(self):
        """Convert the EditHistory instance to a dictionary."""
        return {
            'id': self.id,
            'entry_id': self.entry_id,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'changes': self.changes
        }
