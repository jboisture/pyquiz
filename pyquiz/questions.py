"""
This file contains the logic responsible for parsing the form data
and creating the test, questions and answers.
"""
from pyquiz.models import DBSession
from pyquiz.models import Test, Question, Answer, Course
import colander
import deform


options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def grade_question(question, dbsession, user_answer):
    """
    grades a single question and returns a tuple
    containing a True if the question is correct
    and the credit the question should recieve
    where 1 is full credit and 0 is none.
    """
    if question.question_type == "multipleChoice":
        answer = dbsession.query(Answer).filter(
                            Answer.id == user_answer).first() #load answers
        if answer.correct: #check if the selected answer is correct
            return (True, 1)
    if question.question_type == "selectTrue":
        answers = dbsession.query(Answer).filter(
        Answer.question_id == question.id).all() #load answers
        total_correct = 0
        user_correct = 0
        for a in answers: #find answer that user selected
            if a.correct:
                total_correct += 1
                if str(a.id) in user_answer:
                    user_correct += 1
        if total_correct == user_correct and user_correct == len(user_answer):
            return (True, 1)
    if question.question_type == "shortAnswer":
        answer = Answer(question.id, "username*:"+user_answer, None)
        dbsession.add(answer)
        dbsession.flush
        return (True, 1)
    return (False, 0)        

def create_short_answer_form(question, dbsession, user_choice):
    """create form to take a short answer question"""
    class ShortAnswerSchema(colander.Schema):
        answer = colander.SchemaNode(colander.String(),
                                     title=question.question,
                                     widget = deform.widget.TextInputWidget()
                                     )
    appstruct = {'answer':(user_choice)}
    schema = ShortAnswerSchema()
    return (schema, appstruct)

def create_multiple_choice_form(question, dbsession, user_choice):
    """create form to take a multiple choice form"""
    answers = dbsession.query(Answer).filter(
                      Answer.question_id==question.id).all()
    choices = []
    sorted(answers, key=lambda answer: answer.id)
    for answer in answers: #add all answers to choices so they are in the form
        answer_text = options[answers.index(answer)]+". "+answer.answer
        choices.append((answer.id, answer_text))
    class QuestionSchema(colander.Schema):
        """form class that defines the form used to display the question"""
        answer = colander.SchemaNode(
            colander.String(),
            validator=colander.OneOf([x[0] for x in choices]),
            widget=deform.widget.RadioChoiceWidget(values=choices, 
                                                   null_value = user_choice),
            title=question.question,
            description="Choose you're answer")

    return (QuestionSchema(), None) #create the schema for the form

def create_select_all_form(question, dbsession, user_choices):
    """create form to take a multiple choice form"""
    answers = dbsession.query(Answer).filter(
                      Answer.question_id==question.id).all()
    choices = []
    for answer in answers: #add all answers to choices so they are in the form
        answer_text = options[answers.index(answer)]+". "+answer.answer
        choices.append((str(answer.id), answer_text))

    class SelectAllQuestionSchema(colander.Schema):
        answer = colander.SchemaNode(
            deform.Set(),
            validator=colander.OneOf([x[0] for x in choices]),
            widget=deform.widget.CheckboxChoiceWidget(values=choices, 
                                                   null_values = user_choices),
            title=question.question,
            description="Choose you're answer")
    return (SelectAllQuestionSchema().bind(),None ) #create the schema for the 
                                                    #form

def create_answer(controls, index, question, answer_num, dbsession):
    """
    Reads answer data from the form and creates a answer.
    """
    answerText = str(controls[index+1][1])
    if controls[index+2][0] == 'correct': correct = True
    else: correct = False
    answer = Answer(question.id, answerText, 
                    correct)
    dbsession.add(answer)
    dbsession.flush
    return answer


def create_question(controls, index, question_type, test, number, dbsession):
    """
    Reads question info from form data and creates quesiton.
    Edit this when adding a new question type.
    """
    if question_type == "selectTrue" or question_type == "multipleChoice":
        questionText = str(controls[index+1][1])
        question = Question(True, question_type, questionText, 
                                  test, number)
        dbsession.add(question)
        dbsession.flush()
        return question
    if question_type == "shortAnswer":
        questionText = str(controls[index][1])
        question = Question(False, question_type, questionText,
                                   test, number)
        dbsession.add(question)
        dbsession.flush()
        return None
    return None



def find_question_type(controls, i):
    """
    Parses form data to determine type of question.
    Edit this when adding a new question type.
    """
    if controls[i+1] == ('__start__', u'answers:sequence'):
        i += 2
        correct = 0
        while controls[i] == ('__start__',u'answers:mapping'):
            if controls[i+2][0] == 'correct':
                 correct += 1
                 i += 4
            else: i += 3
        if correct != 1: return "selectTrue"
        if correct == 1: return "multipleChoice"
    return None

def parse_edit_form_data(controls, dbsession, question):
    """
    This function parses the controls from the test creation form
    and puts the newly created test, questions, and answers into
    the database.
    """
    question_id = question.id
    running = True
    foundQuestion = False
    c = 0
    short_answer = False
    num_correct = 0
    num = 0
    n = len(dbsession.query(Answer).filter(
                            Answer.question_id==question.id).all())
    answers = dbsession.query(Answer).filter(
                            Answer.question_id==question.id).all()
    sorted(answers, key=lambda answer: answer.id)
    while c < len(controls):#loop used to traverse the controls creating tests,
                   #questions,and answers
        if (controls[c] == ('__start__', u'answers:mapping')
                             and foundQuestion):
            answerText = str(controls[c+1][1])
            if controls[c+2][0] == 'correct': correct = True
            else: correct = False
            if controls[c+2][0] == 'remove' or controls[c+3][0] == 'remove':
                remove = True
            else: remove = False
            num_correct += correct
            if num < n:
                answer = answers[num]
                answer_found = True
                if remove:
                    dbsession.delete(answer)
                    dbsession.flush()
                    answers.remove(answer)
                    if correct: num_correct -= 1
                    num -= 1
                    n -= 1
                elif (answer.answer != answerText or
                                  answer.correct != correct):
                    answer.question_id = question.id
                    answer.answer = answerText
                    answer.correct = correct
                    dbsession.flush()
                num += 1
            elif not remove:
                answer = Answer(question.id, answerText,
                                correct)
                dbsession.add(answer)
                dbsession.flush()
        if (not foundQuestion and controls[c][0] == 'text'):
            foundQuestion = True
            text = controls[c][1]
            if controls[c+1][0] == 'remove': remove = True
            else: remove = False
            if remove:
                questions = dbsession.query(Question).filter(
                                  Question.test_id == question.test_id).all()
                answers = dbsession.query(Answer).filter(
                                  Answer.question_id == question.id).all()
                for answer in answers:
                    dbsession.delete(answer)
                    dbsession.flush()
                qNum = question.question_num
                dbsession.delete(question)
                dbsession.flush()
                for question in questions:
                    if question.question_num > qNum:
                        question.question_num -= 1
                        dbsession.flush()
            elif text != question.question:
                question.question = text
                dbsession.flush()
        c += 1
    question = dbsession.query(Question).filter(
                               Question.id==question.id).first()
    if question.question_type in ["multipleChoice", "selectTrue"]:
        if num_correct == 1 and question.question_type != "multipleChoice":
            question.question_type = "multipleChoice"
            dbsession.flush()
        if num_correct != 1 and question.question_type != "selectTrue":
            question.question_type = "selectTrue"
            dbsession.flush()


def parse_add_form_data(controls, dbsession, question_num, test):
    """
    This function parses the controls from the test creation form
    and puts the newly created test, questions, and answers into
    the database.
    """
    running = True
    foundTest = False
    short_answer = False
    c = 0
    while c < len(controls):#loop used to traverse the controls creating tests,
                             #questions,and answers
        if controls[c] == ( "__start__", u'questions:mapping'):
            question_type = find_question_type(controls, c+1)
            question_num += 1
            question = create_question(controls, c, question_type, 
                            test.id, question_num, dbsession)
            answer_num = 1
        if controls[c] == ('__start__', u'answers:mapping'):
            create_answer(controls, c, question,
                          answer_num, dbsession)
            answer_num += 1
        if controls[c] == ('__start__',u'short_answer_questions:sequence'):
            short_answer = True
            question_num -= 1
        if controls[c][0] == 'text' and short_answer:
            question_num += 1
            create_question(controls, c, "shortAnswer", 
                            test.id, question_num, dbsession) 
        if controls[c] == ('__end__', u'short_answer_questions:sequence'):
            short_answer = False
        c += 1
                





def parse_form_data(controls, course_id, dbsession):
    """
    This function parses the controls from the test creation form
    and puts the newly created test, questions, and answers into
    the database.
    """
    running = True
    foundTest = False
    c = 0
    short_answer = False
    while c < len(controls):#loop used to traverse the controls creating tests,
                   #questions,and answers
        if controls[c][0] == "name":
            testname = str(controls[c][1])
            newTest = Test(testname, course_id)
            dbsession.add(newTest)
            dbsession.flush()
            foundTest = True
            question_num = 0
            answer_num = 1
        if foundTest:
            if controls[c] == ( "__start__", u'questions:mapping'):
                question_type = find_question_type(controls, c+1)
                question_num += 1
                question = create_question(controls, c, question_type, 
                                newTest.id, question_num, dbsession)
                answer_num = 1
            if controls[c] == ('__start__', u'answers:mapping'):
                create_answer(controls, c, question,
                              answer_num, dbsession)
                answer_num += 1
            if controls[c] == ('__start__',u'short_answer_questions:sequence'):
                short_answer = True
                question_num -= 1
            if controls[c][0] == 'text' and short_answer:
                question_num += 1
                create_question(controls, c, "shortAnswer", 
                                newTest.id, question_num, dbsession) 
            if controls[c] == ('__end__', u'short_answer_questions:sequence'):
                short_answer = False
        c += 1

