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

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

"""class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    test = Column(Integer)
    graded = Column(Boolean)
    question_type = Column(String)
    question = Column(String)

    def __init__(self, test, graded, question_type, question):
        self.test = test
        self.graded = graded
        self.question_type = question_type
        self.question = question

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    question = Column(Integer, ForeignKey("questions.id"))
    answer = Column(String)
    correct = Column(Boolean)

    def __init__(self, question, answer, correct):
        self.question = question
        self.answer = answer
        self.correct = correct


class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    course = Column(String)
    
    def __init__(self, name, course):
        self.name = name
        self.course = course
	

def create_question(test, graded, question_type, question,
                    possible_answers, session):
    question = Question(test, True, "Multiple_Choice", "does this work")
    session.add(question)
    session.flush()
    transaction.commit()
    for answer in possible_answers:
        answer = Answer(question.id, answer[0], answer[1])
        session.add(answer)
        session.flush()
        transaction.commit()"""

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    course = Column(String)
    questions = relationship("Question", backref = 'tests')
    
    def __init__(self, name, course):
        self.name = name
        self.course = course


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    graded = Column(Boolean)
    question_type = Column(String)
    question = Column(String)
    answers = relationship("Answer", backref = "questions")
    question_num = Column(Integer)

    def __init__(self, graded, question_type, question, test_id, question_num):
        self.graded = graded
        self.question_type = question_type
        self.question = question
        self.test_id = test_id
        self.question_num = question_num

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(String)
    correct = Column(Boolean)
    option = Column(String)

    def __init__(self, question_id, answer, correct, option):
        self.question_id = question_id
        self.answer = option + ". " + answer
        self.correct = correct
        self.option = option



def populate():
    pass
    #create_question(test.id, True, "Multiple_Choice", "does this work", 
    #                   [("yes", True),("no",False)], session)
    
def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError:
        DBSession.rollback()
