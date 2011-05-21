from pyquiz.models import DBSession
from pyquiz.models import Test, Question, Answer
from pyramid.request import Request

from colander import MappingSchema
from colander import SequenceSchema
from colander import SchemaNode
from colander import String
from colander import Boolean
from colander import Schema

from deform import ValidationFailure
from deform import Form
from deform import widget

class Answer(MappingSchema):
    text = SchemaNode(String())
    correct = SchemaNode(Boolean())

class Answers(SequenceSchema):
    answers = Answer()

class Question(MappingSchema):
    text = SchemaNode(String())
    answers = Answers()

class Questions(SequenceSchema):
    questions = Question()

class Test(Schema):
    name = SchemaNode(String())
    class_id = SchemaNode(String())
    questions = Questions()

def test_form(request):
    schema = Test()
    myform = Form(schema, buttons=('submit',), use_ajax=True)

    return {'form':myform.render()}

def my_view(request):
    dbsession = DBSession()
    tests = dbsession.query(Test).all()
    for test in tests: test.url = "test?id="+str(test.id)
    return {'tests':tests, 'project':'pyquiz'}

def test(request):
    test_id = int(request.GET["id"])
    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id==test_id).first()
    questions = []
    raw_questions = dbsession.query(Question).filter(Question.test_id==test.id).all()
    for question in raw_questions:
        answers = dbsession.query(Answer).filter(Answer.question_id==question.id).all()
        questions.append((question, answers))
    return {"test":test,"questions":questions}
