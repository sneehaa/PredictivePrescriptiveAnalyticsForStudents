# models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import JSON

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    attendance = db.Column(MutableList.as_mutable(JSON), nullable=False, default=[0]*6)
    semester_marks = db.Column(MutableList.as_mutable(JSON), nullable=True, default=[0]*6)
    preferred_subject = db.Column(db.String(50)) 
    learning_style = db.Column(db.String(50))
    strengths = db.Column(db.String(200))
    weaknesses = db.Column(db.String(200))

    def __init__(self, id, username, password, grade, attendance=None, semester_marks=None):
        self.id = id
        self.username = username
        self.password = password
        self.grade = grade
        self.attendance = attendance if attendance else [0]*6
        self.semester_marks = semester_marks if semester_marks else [0]*6
        self.preferred_subject = None
        self.learning_style = None
        self.strengths = None
        self.weaknesses = None

    def verify_password(self, password):
        return self.password == password

class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False, index=True)
    learning_style = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(500))
    resource_type = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    summary = db.Column(db.String(1000), nullable=True)
    answer = db.Column(db.Text, nullable=True)  # New field for direct answers

    def __init__(self, title, subject, learning_style, description, resource_type, link, summary=None, answer=None):
        self.title = title
        self.subject = subject
        self.learning_style = learning_style
        self.description = description
        self.resource_type = resource_type
        self.link = link
        self.summary = summary
        self.answer = answer

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'learning_style': self.learning_style,
            'description': self.description,
            'resource_type': self.resource_type,
            'link': self.link,
            'summary': self.summary,
            'answer': self.answer
        }
