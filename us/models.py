from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import backref, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from us.database import Base, DbModel
from us.utils import random_string


class User(Base, DbModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(200))
    password = Column(String(50))

    @property
    def json_data(self):
        return {'id': self.id, 'email': self.email}

    def get_projects(self):
        return [m.project for m in self.memberships]

    def can_access(self, project):
        filter = (Membership.user_id==self.id) & (Membership.project_id==project.id)
        return Membership.query.filter(filter).count() > 0

    @classmethod
    def get_all_emails(cls):
        return [u.email for u in cls.query.all()]

    @classmethod
    def create(cls, email, password):
        hashed_password = generate_password_hash(password)
        user = User(email=email, password=hashed_password)
        user.save()
        return user

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id==id).first()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter(cls.email==email).first()


def generate_auth_token():
    return random_string(40)

class Session(Base, DbModel):
    __tablename__ = 'sessions'

    auth_token = Column(String(40), primary_key=True, default=generate_auth_token)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User, backref='sessions', lazy='joined')

    @property
    def json_data(self):
        return {"auth_token": self.auth_token, "user_id": self.user_id}


class Project(Base, DbModel):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))

    @property
    def json_data(self):
        lists = [l.json_data for l in self.story_lists]
        return {"id": self.id, "name": self.name, "lists": lists}

    @classmethod
    def create(cls, name, user):
        project = Project(name=name)
        project.save_and_commit()
        m = Membership.create(user, project)
        UserStoryList.create_default_lists(project)
        return project


class Membership(Base, DbModel):
    __tablename__ = 'memberships'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    
    user = relationship('User', backref=backref('memberships', lazy='joined'))
    project = relationship('Project', lazy='joined', 
            backref=backref('memberships', lazy='joined'))

    @classmethod
    def create(cls, user, project):
        m = cls(user=user, project=project)
        m.save_and_commit()
        return m


class UserStoryList(Base, DbModel):
    __tablename__ = 'userstory_lists'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))

    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship(Project, backref=backref('story_lists', lazy='joined'))

    @property
    def json_data(self):
        stories = [s.json_data for s in self.userstories]
        return {"id": self.id, "name": self.name, "stories": stories}

    @classmethod
    def create_default_lists(cls, project):
        for name in ['Bank', 'Current Iteration', 'Next iteration', 'Archive']:
            cls.create(name, project)

    @classmethod
    def create(cls, name, project):
        list = cls(name=name, project=project)
        list.save_and_commit()
        return list


class UserStory(Base, DbModel):
    __tablename__ = 'userstories'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    points = Column(Integer)

    storylist_id = Column(Integer, ForeignKey('userstory_lists.id'))
    storylist = relationship(UserStoryList, backref='userstories')

    @property
    def json_data(self):
        return {"id": self.id, "title": self.title, "points": self.points}

    @classmethod
    def create(cls, title, points, list):
        story = cls(title=title, points=points, storylist=list)
        story.save_and_commit()
        return story


class AcceptanceTest(Base, DbModel):
    __tablename__ = 'acceptance_tests'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    completed = Column(Boolean, default=False)

    userstory_id = Column(Integer, ForeignKey('userstories.id'))
    userstory = relationship(UserStory, backref=backref('acceptance_tests', 
            lazy='joined'))
