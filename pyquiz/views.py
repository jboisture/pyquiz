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

class AnswerSchema(MappingSchema):
    text = SchemaNode(String())
    correct = SchemaNode(Boolean())

class Answers(SequenceSchema):
    answers = AnswerSchema()

class QuestionSchema(MappingSchema):
    text = SchemaNode(String())
    answers = Answers()

class Questions(SequenceSchema):
    questions = QuestionSchema()

class TestSchema(Schema):
    name = SchemaNode(String())
    class_id = SchemaNode(String())
    questions = Questions()

def test_form(request):
    schema = TestSchema()
    myform = Form(schema, buttons=('submit',), use_ajax=True)

    if 'submit' in request.POST: # detect that the submit button was clicked
        controls = request.POST.items()
        dbsession = DBSession()
        running = True
        foundTest = False
        foundQuestion = False
        c = 0
        while running:
            if controls[c][0] == "name" and controls[c+1][0] == "class_id":
                testname = str(controls[c][1])
                class_id = str(controls[c+1][1])
                newTest = Test(testname, class_id)
                dbsession.add(newTest)
                dbsession.flush()
                foundTest = True
            if foundTest:
                if (controls[c][0] == "__start__" and controls[c][1] == u'questions:mapping'):
                    foundQuestion = True
                    questionText = str(controls[c+1][1])
                    question = Question(True, "Multiple_Choice", questionText, newTest.id)
                    dbsession.add(question)
                    dbsession.flush()
                    foundQuestion = True
                if controls[c] == ('__start__', u'answers:mapping'):
                    answerText = str(controls[c+1][1])
                    if controls[c+2][0] == 'correct': correct = True
                    else: correct = False
                    answer = Answer(question.id, answerText, correct)
                    dbsession.add(answer)
                    dbsession.flush
            if controls[c][0] == 'submit': running = False
            c += 1
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
