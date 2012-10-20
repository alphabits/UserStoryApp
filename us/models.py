from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import backref, relationship

from us.database import Base, DbModel


class User(Base, DbModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(200))
    password = Column(String(50))

    @property
    def json_data(self):
        return {'id': self.id, 'email': self.email}

    @classmethod
    def get_all_emails(cls):
        return [u.email for u in cls.query.all()]

    @classmethod
    def create(cls, email, password):
        user = User(email=email, password=password)
        user.save()
        return user



class Project(Base, DbModel):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))


class Membership(Base, DbModel):
    __tablename__ = 'memberships'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    
    user = relationship('User', backref=backref('memberships', lazy='joined'))
    project = relationship('Project', backref=backref('memberships', lazy='joined'))


class UserStoryList(Base, DbModel):
    __tablename__ = 'userstory_lists'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))


class UserStory(Base, DbModel):
    __tablename__ = 'userstories'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    points = Column(Integer)

    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship(Project, backref=backref('userstories', lazy='joined'))

    storylist_id = Column(Integer, ForeignKey('userstory_lists.id'))
    storylist = relationship(UserStoryList, backref='userstories')


class AcceptanceTest(Base, DbModel):
    __tablename__ = 'acceptance_tests'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    completed = Column(Boolean, default=False)

    userstory_id = Column(Integer, ForeignKey('userstories.id'))
    userstory = relationship(UserStory, backref=backref('acceptance_tests', 
            lazy='joined'))
