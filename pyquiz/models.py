"""this file contains the database models used in pyquiz"""

import transaction

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Boolean
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy.orm import *


from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import Allow
from pyramid.security import Everyone


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Test(Base):
    """the Test class creates the test table used to store each test"""
    __tablename__ = "tests"
    id=Column(Integer, primary_key=True) #id to be used as a primary key
    name = Column(String) #name variable that must be a String
    course = Column(String, ForeignKey("courses.id"))
                                   #course variable that must be a String
    questions = relationship("Question", backref = 'tests') #establishes a 
                            #relationship between the test and it's questions  
    
    def __init__(self, name, course):
        """init function to create a new Test object"""
        self.name = name
        self.course = course


class Question(Base):
    """the Question class creates the question table used to 
       store each question"""
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True) #id to be used as a primary key
    test_id = Column(Integer, ForeignKey("tests.id")) #id of test each
                              #quesiton belongs to. Used to query questions
                              #belonging to a single test
    graded = Column(Boolean) #graded stores whether or not the question will 
                             #be automatically graded upon submission
    question_type = Column(String) #stores what type of question this is
    question = Column(String) #stores the text of the question
    answers = relationship("Answer", backref = "questions", 
                        cascade="all, delete, delete-orphan") #establishes a 
                          #relationship between the quesiton and it's answers
    question_num = Column(Integer) #stores the questions number on the test.

    def __init__(self, graded, question_type, question, test_id, question_num):
        """init function to create a new Quesiton object"""
        self.graded = graded
        self.question_type = question_type
        self.question = question
        self.test_id = test_id
        self.question_num = question_num

class Answer(Base):
    """the Answer class creates the answer table used to store
       each answer"""
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True) #id to be used as a primary key
    question_id = Column(Integer, ForeignKey("questions.id")) #id of quesiton
                                  #that the answer is associated with
    answer = Column(String) #stores the text of the answer
    correct = Column(Boolean) #stores whether or not the answer is correct


    def __init__(self, question_id, answer, correct):
        """init funciton to create a new Answer object"""
        self.question_id = question_id
        self.answer = answer
        self.correct = correct

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    course_id = Column(String)
    course_name = Column(String)
    instructor = Column(String)

    def __init__(self, course_id, course_name, instructor):
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor

    
def initialize_sql(engine):
    """loads the database"""
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession


class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:editors', 'edit') ]
    def __init__(self, request): pass
