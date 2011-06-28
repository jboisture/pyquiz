"""
This file contains all of the views used to control
the pages of pyquiz.
"""

from pyramid.request import Request
from pyramid.httpexceptions import HTTPFound

from schema import TestSchema, EditQuestionSchema
from schema import EditShortAnswerQuestionSchema, AddQuestionsSchema

from pyramid.security import authenticated_userid

from colander import MappingSchema
from colander import SchemaNode
from colander import String

import colander

import deform
from deform import ValidationFailure
from deform import Form
from deform import widget

from questions import *



def view_create_test(request):
    """
    This is the view for the form page where tests are created.
    """
    if authenticated_userid(request) != 'teacher':
        return HTTPFound(location='/')

    course_id = int(request.GET["id"])

    schema = TestSchema()
    myform = Form(schema, buttons=('submit',), 
                  use_ajax=True)  #create the form for the page
    if 'submit' in request.POST: # check if the submit button was clicked
        controls = request.POST.items() # get the data from the form
        dbsession = DBSession()
        parse_form_data(controls, course_id, dbsession)
        return HTTPFound(location='/course?id='+course_id) #redirect to homepage
    return {'form':myform.render()}

def view_add_questions(request):
    if authenticated_userid(request) != 'teacher':
        return HTTPFound(location='/')
    test_id = int(request.GET["id"])
    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id==test_id).first()
    answers = dbsession.query(Question).filter(
                                Question.test_id == test.id).all()
    question_num = len(answers)
    post = request.POST
    if 'add questions' in post:
        controls = request.POST.items() # get the data from the form
        parse_add_form_data(controls, dbsession, question_num, test)
        return HTTPFound(location='/edit_test?id='+str(test_id)) 
                                                    #redirect to homepage
    schema = AddQuestionsSchema()
    myform = Form(schema, buttons=('add questions',), 
                    use_ajax=True)
    return {'form':myform.render()}
    

def view_edit_question(request):
    ###load the question number and test id###
    if authenticated_userid(request) != 'teacher':
        return HTTPFound(location='/')
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

    post = request.POST
    if 'submit changes' in post:
        controls = post.items()
        parse_edit_form_data(controls, dbsession, question)
        return HTTPFound(location='/edit_test?id='+str(test.id))

    if (question.question_type == "multipleChoice" or
        question.question_type == "selectTrue"):
        all_answers = dbsession.query(Answer).filter(
                                       Answer.question_id==question.id).all()
        answers = []
        for answer in all_answers:
            answers.append({"text":answer.answer,'correct':answer.correct})
        schema = EditQuestionSchema()
        appstruct = {'text':(question.question),'answers':answers}
    if question.question_type == "shortAnswer":
        schema = EditShortAnswerQuestionSchema()
        appstruct = {'text':(question.question)}
    form = Form(schema, buttons=('submit changes',), 
                  use_ajax=True)
    return {"test":test,'form':form.render(appstruct), 'question': question}

def view_delete_test(request):
    if authenticated_userid(request) != 'teacher':
        return HTTPFound(location='/')
    test_id = int(request.GET["id"])
    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id == test_id).first()
    post = request.POST
    if 'no' in post:
        return HTTPFound(location='/edit_test?id='+str(test.id))
    if 'yes' in post:
        questions = dbsession.query(Question).filter(
                                    Question.test_id == test.id).all()
        for question in questions:
             answers = dbsession.query(Answer).filter(
                                       Answer.question_id == question.id).all()
             for answer in answers:
                 dbsession.delete(answer)
                 dbsession.flush()
             dbsession.delete(question)
             dbsession.flush()
        dbsession.delete(test)
        dbsession.flush()
        return HTTPFound(location='/')
    message = []
    message.append("Are you sure you want to delete this test?")
    message.append("Test: " + test.name)
    message.append("Course: " + test.course)
    class deleteForm(colander.Schema):
        pass
    schema = deleteForm()
    form = deform.Form(schema, buttons=('yes','no'))
    return {'form':form.render(), 'message':message}
    

def view_edit_test(request):
    if authenticated_userid(request) != 'teacher':
        return HTTPFound(location='/')
    test_id = int(request.GET["id"]) #get test id

    ###load test and questions from database###
    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id==test_id).first()
    all_questions = dbsession.query(Question).filter(
                                    Question.test_id==test.id).all()
    num_questions = len(all_questions)

    delete_link = "/delete_test?id="+str(test.id)
    add_link = "/add_questions?id="+str(test.id)

    ###create a list of questions, each question will be of the form###
    ###("question #: QUESTION STATUS", "/test?id=#;question#")###
    questions = []
    for i in range(num_questions):
        questions.append(("question "+str(i+1),
                 "/edit_question?id="+str(test_id)+";question="+str(i+1)))
    
    return {"test":test,"questions":questions,
            'delete_link':delete_link,'add_link':add_link}

def view_choose_test(request):
    """
    View that controls page used to select a test to edit
    """
    if authenticated_userid(request) != 'teacher':
        return HTTPFound(location='/')
    if 'current_test' in request.session.keys(): 
        request.session.pop('current_test')
    course_id = int(request.GET["id"])
    dbsession = DBSession()
    tests = dbsession.query(Test).filter(Test.course == course_id).all()
    for test in tests: 
        test.url = "edit_test?id="+str(test.id) 
                                        #create url for each test to pass to 
                                        #the template
    course = dbsession.query(Course).filter(Course.id == course_id).first()
    messages = []
    messages.append("Course: "+course.course_name)
    instructors = course.instructor.split('%&')
    m = "Instructor(s): " + instructors[0]
    i = 1
    while i < len(instructors):
        m += ', ' + instructors[i]
        i += 1
    messages.append(m)
    messages.append('There are currently '+str(len(tests))+' tests:')
    return {'tests':tests, 'messages':messages}


def view_index(request):
    """
    View associated with the home page of the app.
    """
    if authenticated_userid(request) == None:
        return HTTPFound(location='/')
    if 'current_test' in request.session.keys(): 
        request.session.pop('current_test') #remove current_test from session
    userinfo = request.session['user']
    messages = []
    messages.append("Welcome " + userinfo['name'] + " to pyquiz.")
    dbsession = DBSession()
    if authenticated_userid(request) == 'teacher':
        messages.append('You are currently teaching the following classes:')
    if authenticated_userid(request) == 'student':
        messages.append('You are currently enrolled in the following classes:')
    courses = []
    for c in userinfo['courses']:
        courses.append(dbsession.query(Course).filter(
                                       Course.course_id == c[0]).first())
    messages.append('')
    if len(courses) == 0:
        messages[2] == 'You have no classes'
    for course in courses:
        course.url = 'course?id='+str(course.id)
    return {'messages': messages, 'courses': courses}
        


def view_course(request):
    if authenticated_userid(request) == None:
        return HTTPFound(location='/')
    if 'current_test' in request.session.keys(): 
        request.session.pop('current_test')
    course_id = int(request.GET["id"])
    dbsession = DBSession()
    course = dbsession.query(Course).filter(Course.id == course_id).first()
    tests = dbsession.query(Test).filter(Test.course == course_id).all() #load all tests
    for test in tests: 
        test.url = "test?id="+str(test.id) #create url for each test to pass to
                                           #the template
    messages = []
    messages.append("Course: "+course.course_name)
    instructors = course.instructor.split('%&')
    m = "Instructor(s): " + instructors[0]
    i = 1
    while i < len(instructors):
        m += ', ' + instructors[i]
        i += 1
    messages.append(m)
    messages.append('There are '+str(len(tests))+' tests to take:')
    links = []
    if authenticated_userid(request) == 'teacher':
        links.append(('/create_test?id='+str(course.id),
                                   'Create A New Test'))
        links.append(('/choose_test?id='+str(course.id),
                               'Edit An Existing Test'))
    return {'tests':tests, 'messages':messages, 'links':links}




def view_question(request):
    """
    The view for the question page to answer a single question of a test.
    """
    if authenticated_userid(request) == None:
        return HTTPFound(location='/')
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
        if question.question_type == "shortAnswer":
            for control in controls:
                if control[0] == 'answer':
                    answer = str(control[1])
        if question.question_type == "multipleChoice":
            for control in controls:
                if control[0] == 'deformField1':
                    answer = str(control[1])
        if question.question_type == "selectTrue":
            answer = []
            for control in controls:
                if control[0] == 'checkbox':
                    answer.append(control[1])
        session["current_test"][str(question_num)]=answer 
                                            #store selected answer
        if 'next question' in post:
            return HTTPFound(location='/question?id='+str(test.id)+
                             ';question='+str(question_num+1))
        if 'review test' in post: #check if it was the last question
                                  #if so redirect to the test's submit page
            return HTTPFound(location='/test?id='+str(test.id))

    ###create the question's form###
    if question.question_type == "multipleChoice":
        schema = create_multiple_choice_form(question, 
                                       dbsession, user_choice)
    if question.question_type == "selectTrue":
        schema = create_select_all_form(question,
                                       dbsession, user_choice)
    if question.question_type == "shortAnswer":
        schema = create_short_answer_form(question, dbsession, user_choice)


    if question_num == total_questions: #check if this is the last question
        form = deform.Form(schema[0],
                           buttons=('review test',))
    else:
        form = deform.Form(schema[0],
                           buttons=('next question',))
    if question.question_type == "shortAnswer":
        return {"test":test,'form':form.render(schema[1]),
                'link':'/test?id='+str(test.id)}
    return {"test":test,'form':form.render(), 'link':'/test?id='+str(test.id)}

    

def view_test(request):
    """
    This view displays the submit page that shows and overview of the test
    and allows the test taker to submit the test for grading.
    """
    if authenticated_userid(request) == None:
        return HTTPFound(location='/')
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
    if authenticated_userid(request) == None:
        return HTTPFound(location='/')

    ###load the test and it's questions froms the database###
    test_id = int(request.GET["id"])
    dbsession = DBSession()
    test = dbsession.query(Test).filter(Test.id==test_id).first()
    questions = dbsession.query(Question).filter(
                                    Question.test_id==test.id).all()
    num_questions = len(questions)

    ###create the "current_test" in session if it is not already there###
    if "current_test" not in request.session.keys():
        return HTTPFound(location='/test?id='+str(test.id))
    current_test = request.session["current_test"]

    ###grade the test submitted test###
    correct = 0
    num_graded = 0
    session = request.session
    question_messages = [] #quesiton_messages will contain reports for the
                           #template about if each quesiton is correct or not
    for question in questions:#loop through and grade each question
        if question.graded: num_graded += 1
        q_num = question.question_num
        if str(q_num) in current_test.keys(): #make sure user selected
                                            #an answer to the question
            user_answer=current_test[str(q_num)]
                                            #get users answer for the question
            grade = grade_question(question, dbsession, user_answer)
            if question.graded:
                if grade[0]:
                    correct += grade[1]
                    question_messages.append(str(q_num)+". Correct")
                else: question_messages.append(str(q_num)+". INCORRECT")
            else: question_messages.append(str(q_num)+". Not Graded")
        else: question_messages.append(str(q_num)+". INCORRECT")

    ###create a report to display the result of the test###
    if num_graded > 0:
        message ="You got "+str(correct)+" out of "+str(num_graded)+" correct."
        message =message +"(" + str(int(1000.0*correct/num_graded)/10.0) + "%)"
    else:
        message="There were no graded questions."
    session.pop("current_test") #remove "current_test" from sesssion

    return {"test":test, "message":message,"questions":question_messages}
        
                                  
   
