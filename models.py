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
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.String(1000), nullable=True)  # Ensure this line is present

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'summary': self.summary  # Include summary in dict
        }
