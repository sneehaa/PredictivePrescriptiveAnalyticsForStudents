# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# class Resource(db.Model):
#     __tablename__ = 'resources'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(200), nullable=False, index=True)
#     subject = db.Column(db.String(50), nullable=False, index=True)
#     learning_style = db.Column(db.String(50), nullable=False, index=True)
#     description = db.Column(db.String(500))
#     resource_type = db.Column(db.String(50), nullable=False)
#     link = db.Column(db.String(500), nullable=False)
#     summary = db.Column(db.String(1000), nullable=True)
#     answer = db.Column(db.Text, nullable=True)  # New field for direct answers

#     def __init__(self, title, subject, learning_style, description, resource_type, link, summary=None, answer=None):
#         self.title = title
#         self.subject = subject
#         self.learning_style = learning_style
#         self.description = description
#         self.resource_type = resource_type
#         self.link = link
#         self.summary = summary
#         self.answer = answer

#     def to_dict(self):
#         return {
#             'id': self.id,
#             'title': self.title,
#             'subject': self.subject,
#             'learning_style': self.learning_style,
#             'description': self.description,
#             'resource_type': self.resource_type,
#             'link': self.link,
#             'summary': self.summary,
#             'answer': self.answer
#         }
