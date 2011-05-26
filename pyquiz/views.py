from pyquiz.models import DBSession
from pyquiz.models import Test, Question, Answer
from pyramid.request import Request
from pyramid.httpexceptions import HTTPFound

from schema import AnswerSchema
from schema import Answers
from schema import QuestionSchema
from schema import Questions
from schema import TestSchema

import colander
from colander import MappingSchema
from colander import SequenceSchema
from colander import SchemaNode
from colander import String
from colander import Boolean
from colander import Schema

import deform
from deform import ValidationFailure
from deform import Form
from deform import widget

options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

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
                question_num = 1
            if foundTest:
                if (controls[c][0] == "__start__" and controls[c][1] == 
                           u'questions:mapping'):
                    foundQuestion = True
                    questionText = str(controls[c+1][1])
                    question = Question(True, "Multiple_Choice", questionText, 
                                        newTest.id, question_num)
                    question_num += 1
                    dbsession.add(question)
                    dbsession.flush()
                    foundQuestion = True
                    answer_num = 1
                if controls[c] == ('__start__', u'answers:mapping'):
                    answerText = str(controls[c+1][1])
                    if controls[c+2][0] == 'correct': correct = True
                    else: correct = False
                    answer = Answer(question.id, answerText, 
                                    correct, options[answer_num-1])
                    answer_num += 1
                    dbsession.add(answer)
                    dbsession.flush
            if controls[c][0] == 'submit': running = False
            c += 1
        return HTTPFound(location='/')
    return {'form':myform.render()}



def my_view(request):
    dbsession = DBSession()
    tests = dbsession.query(Test).all()
    for test in tests: test.url = "test?id="+str(test.id)
    return {'tests':tests, 'project':'pyquiz'}



def test(request):
    test_id = int(request.GET["id"])
    try:
        question_num = int(request.GET["question"])
    except:
        question_num = 1
               

    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id==test_id).first()
    all_questions = dbsession.query(Question).filter(
                                    Question.test_id==test.id).all()
    total_questions = len(all_questions)
    for q in all_questions:
        if q.question_num == question_num:
            question = q
    answers = dbsession.query(Answer).filter(
                      Answer.question_id==question.id).all()
    post = request.POST
    if 'review test' in post or 'next question' in post:
        controls = post.items()
        session = request.session
        if "current_test" not in session.keys() or (
                          session["current_test"]["name"] != test.name):
            session["current_test"] = {"name": test.name}
        answer = "na"
        i = 0
        for control in controls:
            if control[0] == 'deformField1':
               answer = str(control[1])
        session["current_test"][str(question_num)] = answer
        if 'next question' in post:
            return HTTPFound(location='/test?id='+str(test.id)+
                             ';question='+str(question_num+1))
        if 'review test' in post:
            return HTTPFound(location='/submit?id='+str(test.id))
    choices = []
    for answer in answers:
        choices.append((answer.option, answer.answer))
    class QuestionForm(colander.Schema):
        answer = colander.SchemaNode(
            colander.String(),
            validator=colander.OneOf([x[0] for x in choices]),
            widget=deform.widget.RadioChoiceWidget(values=choices),
            title=question.question,
            description="Choose you're answer")
    schema = QuestionForm()
    if question_num == total_questions:
        form = deform.Form(schema, buttons=('review test',))
    else:
        form = deform.Form(schema, buttons=('next question',))
    return {"test":test,'form':form.render(),'link':'/submit?id='+str(test.id)}

def submit_test(request):
    test_id = int(request.GET["id"])
    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id==test_id).first()
    all_questions = dbsession.query(Question).filter(
                                    Question.test_id==test.id).all()
    num_questions = len(all_questions)
    current_test = request.session["current_test"]
    questions = []
    for i in range(num_questions):
        if str(i+1) not in current_test.keys():
            questions.append(("question "+str(i+1)+": NOT ANSWERED",
                     "/test?id="+str(test_id)+";question="+str(i+1)))
        else:
            if current_test[str(i+1)] == "na":
                questions.append(("question "+str(i+1)+": NOT ANSWERED",
                         "/test?id="+str(test_id)+";question="+str(i+1)))
            else:
                questions.append(("question "+str(i+1)+": Answered",
                         "/test?id="+str(test_id)+";question="+str(i+1)))
    
    return {"test":test,"questions":questions,"link":"/grade?id="+str(test_id)}

def grade_test(request):
    test_id = int(request.GET["id"])
    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id==test_id).first()
    all_questions = dbsession.query(Question).filter(
                                    Question.test_id==test.id).all()
    num_questions = len(all_questions)
    current_test = request.session["current_test"]
    correct = 0
    session = request.session
    question_messages = []
    for i in range(num_questions):
        user_answer = current_test[str(i+1)]
        questions = dbsession.query(Question).filter(
                                  Question.test_id == test.id).all()
        for q in questions:
            if q.question_num == i+1: question = q
        answers = dbsession.query(Answer).filter(
                                  Answer.question_id == question.id).all()
        for a in answers:
            if a.option == user_answer: answer = a
        if answer.correct:
            correct += 1
            question_messages.append(str(i+1)+". Correct")
        else: question_messages.append(str(i+1)+". INCORRECT")
    message = "You got "+str(correct)+" out of "+str(num_questions)+" correct."
    message = message + "(" + str(int(1000.0*correct/num_questions)/10.0) + "%)"
    return {"test":test, "message":message,"questions":question_messages}
        
                                  
   
