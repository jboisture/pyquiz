"""
This file contains the logic responsible for parsing the form data
and creating the test, questions and answers.
"""
from pyquiz.models import DBSession
from pyquiz.models import Test, Question, Answer
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
        answers = dbsession.query(Answer).filter(
        Answer.question_id == question.id).all() #load answers
        for a in answers: #find answer that user selected
            if a.option == user_answer: answer = a
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
                if a.option in user_answer:
                    user_correct += 1
        if total_correct == user_correct and user_correct == len(user_answer):
            return (True, 1)
    return (False, 0)        

def create_multiple_choice_form(question, dbsession, user_choice):
    """create form to take a multiple choice form"""
    answers = dbsession.query(Answer).filter(
                      Answer.question_id==question.id).all()
    choices = []
    for answer in answers: #add all answers to choices so they are in the form
        choices.append((answer.option, answer.answer))
    class QuestionSchema(colander.Schema):
        """form class that defines the form used to display the question"""
        answer = colander.SchemaNode(
            colander.String(),
            validator=colander.OneOf([x[0] for x in choices]),
            widget=deform.widget.RadioChoiceWidget(values=choices, 
                                                   null_value = user_choice),
            title=question.question,
            description="Choose you're answer")
    return QuestionSchema() #create the schema for the form

def create_select_true_form(question, dbsession, user_choices):
    """create form to take a multiple choice form"""
    answers = dbsession.query(Answer).filter(
                      Answer.question_id==question.id).all()
    choices = []
    for answer in answers: #add all answers to choices so they are in the form
        choices.append((answer.option, answer.answer))

    class SelectTrueQuestionSchema(colander.Schema):
        answer = colander.SchemaNode(
            deform.Set(),
            validator=colander.OneOf([x[0] for x in choices]),
            widget=deform.widget.CheckboxChoiceWidget(values=choices, 
                                                   null_values = user_choices),
            title=question.question,
            description="Choose you're answer")
    return SelectTrueQuestionSchema().bind() #create the schema for the form

def create_answer(controls, index, question, answer_num, dbsession):
    """
    Reads answer data from the form and creates a answer.
    """
    answerText = str(controls[index+1][1])
    if controls[index+2][0] == 'correct': correct = True
    else: correct = False
    answer = Answer(question.id, answerText, 
                    correct, options[answer_num-1])
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
            if controls[c] == ( "__start__", u'questions:mapping'):
                question_type = find_question_type(controls, c+1)
                question = create_question(controls, c, question_type, 
                                newTest.id, question_num, dbsession) 
                question_num += 1
                foundQuestion = True
                answer_num = 1
            if controls[c] == ('__start__', u'answers:mapping'):
                answer = create_answer(controls, c, question,
                                       answer_num, dbsession)
                answer_num += 1
        if controls[c][0] == 'submit': running = False
        c += 1

