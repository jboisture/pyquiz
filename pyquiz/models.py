"""this file contains the database models used in pyquiz"""

import transaction

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import Boolean
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import *

import datetime


from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import Allow
from pyramid.security import Everyone


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class TakenTest(Base):
    """
    The TakenTest class creates the takentests table that stores information about
    all of the tests that have been taken by students.
    """
    __tablename__ = "takentests"
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer) #id of test each
    username = Column(String)
    student_name = Column(String)
    number_graded_questions = Column(Integer)
    correct_graded_questions = Column(Integer)
    ungraded_answers = relationship("TakenAnswer", backref = "questions", 
                           cascade="all, delete, delete-orphan")
    time_submitted = Column(String)
    has_ungraded = Column(Boolean)
    attempts = Column(Integer)
    
    def __init__(self, test_id, username, student_name, number_graded_questions, correct_graded_questions, has_ungraded, attempts):
        time = datetime.datetime.now()
        if time.minute < 10:
            time_submitted = str(time.month) + "/" + str(time.day) + '/' + str(time.year) + " at " + str(time.hour%12) + ":0" + str(time.minute)
        else:
            time_submitted = str(time.month) + "/" + str(time.day) + '/' + str(time.year) + " at " + str(time.hour%12) + ":" + str(time.minute)
        if time.hour%12 == 1: time_submitted += "PM"
        else:time_submitted += "AM"
        self.time_submitted = time_submitted
        self.test_id = test_id
        self.username = username
        self.student_name = student_name
        self.number_graded_questions = number_graded_questions
        self.correct_graded_questions = correct_graded_questions
        self.has_ungraded = has_ungraded
        self.attempts = attempts

class TakenAnswer(Base):
    """
    The TakenAnswer class creates the takenanswers table that stores information about
    all of the answers submitted by students.
    """
    __tablename__ = "takenanswers"
    id = Column(Integer, primary_key=True)
    takentest_id = Column(Integer, ForeignKey("takentests.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    question_num = Column(Integer)
    user_answer = Column(String)
    graded = Column(Boolean)
    correct = Column(Boolean)

    def __init__(self, takentest_id, question, user_answer, graded, correct):
        self.takentest_id = takentest_id
        self.question_id = question.id
        self.question_num = question.question_num
        self.user_answer = user_answer
        self.graded = graded
        self.correct = correct

class Test(Base):
    """the Test class creates the test table used to store each test"""
    __tablename__ = "tests"
    id=Column(Integer, primary_key=True) #id to be used as a primary key
    name = Column(String) #name variable that must be a String
    course = Column(String, ForeignKey("courses.id"))
                                   #course variable that must be a String
    questions = relationship("Question", backref = 'tests') #establishes a 
                            #relationship between the test and it's questions
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    attempts = Column(Integer)
    test_type = Column(String)
    schooltool_id = Column(String)
    
    def __init__(self, name, course, start_time, end_time,
                                      attempts, test_type, schooltool_id):
        """init function to create a new Test object"""
        self.name = name
        self.course = course
        self.start_time = start_time
        self.end_time = end_time
        self.attempts = attempts
        self.test_type
        self.schooltool_id = schooltool_id

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
    image = Column(String)

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
    """
    The Course class creates the courses table that stores information about
    all of the courses.
    """
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    term_id = Column(String)
    course_id = Column(String)
    course_name = Column(String)
    instructor = Column(String)

    def __init__(self, term_id, course_id, course_name, instructor):
        self.term_id = term_id
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
