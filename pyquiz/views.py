"""
This file contains all of the views used to control
the pages of pyquiz.
"""

from pyquiz.models import DBSession
from pyquiz.models import Test, Question, Answer
from pyramid.request import Request
from pyramid.httpexceptions import HTTPFound

from schema import TestSchema

import colander

import deform
from deform import ValidationFailure
from deform import Form
from deform import widget

options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def parse_form_data(controls, dbsession):
    """
    This function parses the controls from the test creation form
    and puts the newly created test, questions, and answers into
    the database.
    """

    running = True
    foundTest = False
    foundQuestion = False
    c = 0
    while running: #loop used to traverse the controls creating tests,
                   #questions,and answers
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


def view_create_test(request):
    """
    This is the view for the form page where tests are created.
    """

    schema = TestSchema()
    myform = Form(schema, buttons=('submit',), 
                  use_ajax=True)  #create the form for the page
    if 'submit' in request.POST: # check if the submit button was clicked
        controls = request.POST.items() # get the data from the form
        dbsession = DBSession()
        parse_form_data(controls, dbsession)
        return HTTPFound(location='/') #redirect to homepage
    return {'form':myform.render()}



def view_index(request):
    """
    View associated with the home page of the app.
    """
    session = request.session
    if 'current_test' in session.keys(): 
        session.pop("current_test") #remove current_test from session
    dbsession = DBSession()
    tests = dbsession.query(Test).all() #load all tests
    for test in tests: 
        test.url = "test?id="+str(test.id) #create url for each test to pass to 
                                           #the template
    return {'tests':tests, 'project':'pyquiz'}



def view_question(request):
    """
    The view for the question page to answer a single question of a test.
    """

    ###load the question number and test id###
    test_id = int(request.GET["id"])
    quesiton_num = 1
    try:
        question_num = int(request.GET["question"])
    except:
        question_num = 1

    ###load the test and it's questions and their answers from the database###
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

    ###create "current_test" in the session object###
    session = request.session
    user_choice = ''
    if "current_test" not in session.keys() or (
                      session["current_test"]["name"] != test.name):
            session["current_test"] = {"name": test.name}

    ###load any previously selected answer to this question###
    if str(question_num) in session['current_test'].keys():
        user_choice = session['current_test'][str(question_num)]

    ###check if a question was submited and put the answer in the session###
    post = request.POST
    if 'review test' in post or 'next question' in post:
        controls = post.items()
        answer = "na"
        i = 0
        for control in controls:
            if control[0] == 'deformField1':
               answer = str(control[1])
        session["current_test"][str(question_num)]=answer #store selected answer
        if 'next question' in post:
            return HTTPFound(location='/question?id='+str(test.id)+
                             ';question='+str(question_num+1))
        if 'review test' in post: #check if it was the last question
                                  #if so redirect to the test's submit page
            return HTTPFound(location='/test?id='+str(test.id))

    ###create the questions form###
    choices = []
    for answer in answers: #add all answers to choices so they are in the form
        choices.append((answer.option, answer.answer))
    class QuestionForm(colander.Schema):
        """form class that defines the form used to display the question"""
        answer = colander.SchemaNode(
            colander.String(),
            validator=colander.OneOf([x[0] for x in choices]),
            widget=deform.widget.RadioChoiceWidget(values=choices, 
                                                   null_value = user_choice),
            title=question.question,
            description="Choose you're answer")
    schema = QuestionForm() #create the schema for the form
    if question_num == total_questions: #check if this is the last question
        form = deform.Form(schema, buttons=('review test',))
    else:
        form = deform.Form(schema, buttons=('next question',))

    return {"test":test,'form':form.render(),'link':'/test?id='+str(test.id)}

def view_test(request):
    """
    This view displays the submit page that shows and overview of the test
    and allows the test taker to submit the test for grading.
    """

    test_id = int(request.GET["id"]) #get test id

    ###load test and questions from database###
    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id==test_id).first()
    all_questions = dbsession.query(Question).filter(
                                    Question.test_id==test.id).all()
    num_questions = len(all_questions)

    ###create the "current_test" in session if it is not already there###
    if "current_test" not in request.session.keys():
        request.session["current_test"] = {"name": test.name}
    current_test = request.session["current_test"]

    ###create a list of questions, each question will be of the form###
    ###("question #: QUESTION STATUS", "/test?id=#;question#")###
    questions = []
    for i in range(num_questions):
        if (str(i+1) not in current_test.keys()):
            questions.append(("question "+str(i+1)+": NOT ANSWERED",
                     "/question?id="+str(test_id)+";question="+str(i+1)))
        else:
            if current_test[str(i+1)] == "na":
                questions.append(("question "+str(i+1)+": NOT ANSWERED",
                         "/question?id="+str(test_id)+";question="+str(i+1)))
            else:
                questions.append(("question "+str(i+1)+": Answered",
                         "/question?id="+str(test_id)+";question="+str(i+1)))
    
    return {"test":test,"questions":questions,"link":"/grade?id="+str(test_id)}

def view_grade_test(request):
    """
    This view grades tests and reports the grade in the grade page.
    """

    ###load the test and it's questions froms the database###
    test_id = int(request.GET["id"])
    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id==test_id).first()
    questions = dbsession.query(Question).filter(
                                    Question.test_id==test.id).all()
    num_questions = len(questions)

    ###create the "current_test" in session if it is not already there###
    if "current_test" not in request.session.keys():
        request.session["current_test"] = {"name": test.name}
    current_test = request.session["current_test"]

    ###grade the test submitted test###
    correct = 0
    session = request.session
    question_messages = [] #quesiton_messages will contain reports for the
                           #template about if each quesiton is correct or not
    for i in range(num_questions): #loop through and grade each question
        if str(i+1) in current_test.keys(): #make sure user selected
                                            #an answer to the question
            user_answer=current_test[str(i+1)]#get users answer for the question
            for q in questions:
                if q.question_num == i+1: question = q
            answers = dbsession.query(Answer).filter(
                          Answer.question_id == question.id).all() #load answers
            for a in answers: #find answer that user selected
                if a.option == user_answer: answer = a
            if answer.correct: #check if the selected answer is correct
                correct += 1
                question_messages.append(str(i+1)+". Correct")
            else: question_messages.append(str(i+1)+". INCORRECT")
        else: question_messages.append(str(i+1)+". INCORRECT")

    ###create a report to display the result of the test###
    message = "You got "+str(correct)+" out of "+str(num_questions)+" correct."
    message = message + "(" + str(int(1000.0*correct/num_questions)/10.0) + "%)"
    session.pop("current_test") #remove "current_test" from sesssion

    return {"test":test, "message":message,"questions":question_messages}
        
                                  
   
