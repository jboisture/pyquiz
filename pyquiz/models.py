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

    def __init__(self, graded, question_type, question, test_id):
        self.graded = graded
        self.question_type = question_type
        self.question = question
        self.test_id = test_id

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(String)
    correct = Column(Boolean)

    def __init__(self, question_id, answer, correct):
        self.question_id = question_id
        self.answer = answer
        self.correct = correct

def make_test():
    session = DBSession()
    if len(session.query(Test).all()) < 1:
        test = Test("This is a test", "Math")
        session.add(test)
        session.flush()
        question = Question(True, "Multiple_Choice", "does this work", test.id)
        session.add(question)
        session.flush()
        answer = Answer(question.id, "yes", True)
        answer2 = Answer(question.id, "no", False)
        session.add(answer)
        session.add(answer2)
        session.flush()
        transaction.commit()
    if len(session.query(Test).all()) < 2:
        test = Test("This is the second test", "Math")
        session.add(test)
        session.flush()
        question = Question(True, "Multiple_Choice", "does this work again", test.id)
        session.add(question)
        session.flush()
        answer = Answer(question.id, "yes", True)
        answer2 = Answer(question.id, "no", False)
        answer3 = Answer(question.id, "maybe", False)
        session.add(answer)
        session.add(answer2)
        session.add(answer3)
        session.flush()
        transaction.commit()
    if len(session.query(Test).all()) < 3:
        test = Test("This test should have 2 questions", "Math")
        session.add(test)
        session.flush()
        question = Question(True, "Multiple_Choice", "does this work again", test.id)
        session.add(question)
        session.flush()
        answer = Answer(question.id, "yes", True)
        answer2 = Answer(question.id, "no", False)
        answer3 = Answer(question.id, "maybe", False)
        session.add(answer)
        session.add(answer2)
        session.add(answer3)
        session.flush()
        question2 = Question(True, "Multiple_Choice", "are there two questions", test.id)
        session.add(question2)
        session.flush()
        answer = Answer(question2.id, "yes", True)
        answer2 = Answer(question2.id, "no", False)
        session.add(answer)
        session.add(answer2)
        session.flush()
        transaction.commit()
    


def populate():
    make_test()
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
