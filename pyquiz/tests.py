"""
tests currently broken because there is a problem trying remaining logged in
in the tests.
"""
import unittest
from pyramid import testing

from models import Test, Question, Answer, initialize_sql
from webob.multidict import MultiDict


from login import *
from testingData import *

from pyramid.security import authenticated_userid

def _initTestingDB():
    from models import DBSession
    from models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://')
    return initialize_sql(engine)

def _clearTestingDB(session):
    from models import Test, Question, Answer
    tests = session.query(Test).all()
    for test in tests:
        session.delete(test)
        session.flush()
    answers = session.query(Answer).all()
    for answer in answers:
        session.delete(answer)
        session.flush()
    questions = session.query(Question).all()
    for question in questions:
        session.delete(question)
        session.flush()

def _createFormData(data):
    POST = MultiDict()
    for d in data:
        POST.add(d[0], d[1])
    return POST

def _populateDB(session):
    test = Test("Math Test", "Math 101")
    session.add(test)
    session.flush()
    test2 = Test("Math Test 2", "Math 102")
    session.add(test2)
    session.flush()
    question = Question(True, "multipleChoice", "1+1 = ?", test.id, 1)
    session.add(question)
    session.flush()
    answer = Answer(question.id, "1", False)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "2", True)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "3", False)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "4", False)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "5", False)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "6", False)
    session.add(answer)
    session.flush()
    question = Question(True, "selectTrue", "X^2 = 1", test.id, 2)
    session.add(question)
    session.flush()
    answer = Answer(question.id, "-1", True)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "1", True)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "2", False)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "3", False)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "4", False)
    session.add(answer)
    session.flush()
    answer = Answer(question.id, "5", False)
    session.add(answer)
    session.flush()
    question = Question(False, 
                        "shortAnswer",
                        "What is you're name?", 
                        test.id, 3)
    session.add(question)
    session.flush()


class ViewCreateTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)
        
    def _callFUT(self, formData):
        request = testing.DummyRequest(_createFormData(formData))
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session = {'user': {'username': 'teacher', 'courses': [('101', 'Math 101'), ('102', 'Math 102'), ('103', 'Math 103')], 'role': 'teacher', 'name': 'teacher teacher'}}
        request.GET['id']=1
        from views import view_create_test
        return view_create_test(request)

    def test_view_create(self):

        info = self._callFUT("")
        self.assertTrue('form' in info.keys())

    def test_create_multipleChoice(self):   ###Test creating a multipleChoice question with one correct answer###
        info = self._callFUT(multipleChoiceData)
        tests = self.session.query(Test).all()
        self.assertEqual(1, len(tests))
        test = tests[0]
        self.assertEqual("Math Test", test.name)
        questions = self.session.query(Question).all()
        self.assertEqual(1, len(questions))
        question = questions[0]
        self.assertEqual(question.question, "1+1 = ?")
        self.assertEqual(question.question_type, "multipleChoice")
        answers = self.session.query(Answer).all()
        self.assertEqual(2, len(answers))
        self.assertEqual('1', answers[0].answer)
        self.assertFalse(answers[0].correct)
        self.assertEqual('2', answers[1].answer)
        self.assertTrue(answers[1].correct)
        _clearTestingDB(self.session)

    def test_create_selectTrue(self):###Test creating a selectTrue question with more than one correct answer###
        info = self._callFUT(selectTrueData)
        tests = self.session.query(Test).all()
        self.assertEqual(1, len(tests))
        test = tests[0]
        self.assertEqual("Math Test", test.name)
        questions = self.session.query(Question).all()
        self.assertEqual(1, len(questions))
        question = questions[0]
        self.assertEqual(question.question, "1+1 = ?")
        self.assertEqual(question.question_type, "selectTrue")
        answers = self.session.query(Answer).filter(
                                    Answer.question_id == question.id).all()
        self.assertEqual(2, len(answers))
        self.assertEqual('1', answers[0].answer)
        self.assertTrue(answers[0].correct)
        self.assertEqual('2', answers[1].answer)
        self.assertTrue(answers[1].correct)
        _clearTestingDB(self.session)

    def test_create_shortAnswer(self):###Test creating a shortAnswer question with more than one correct answer##
        info = self._callFUT(shortAnswerData)
        tests = self.session.query(Test).all()
        self.assertEqual(1, len(tests))
        test = tests[0]
        self.assertEqual("Short Answer", test.name)
        questions = self.session.query(Question).all()
        self.assertEqual(1, len(questions))
        question = questions[0]
        self.assertEqual(question.question, "What is you're name?")
        self.assertEqual(question.question_type, "shortAnswer")
        answers = self.session.query(Answer).all()
        self.assertEqual(0, len(answers))
        _clearTestingDB(self.session)

    def test_create_all(self):###Test creating one of each type of question###
        info = self._callFUT(allTypesData)
        tests = self.session.query(Test).all()
        self.assertEqual(1, len(tests))
        test = tests[0]
        self.assertEqual("All Types", test.name)
        questions = self.session.query(Question).all()
        self.assertEqual(3, len(questions))
        self.assertEqual("multipleChoice", questions[0].question_type)
        self.assertEqual("selectTrue", questions[1].question_type)
        self.assertEqual("shortAnswer", questions[2].question_type)
        self.assertEqual('1+1 = ?', questions[0].question)
        self.assertEqual('x^2 = 1', questions[1].question)
        self.assertEqual("What is you're name?", questions[2].question)
        self.assertEqual(1, questions[0].id)
        self.assertEqual(2, questions[1].id)
        self.assertEqual(3, questions[2].id)
        answers = self.session.query(Answer).filter(
                                    Answer.question_id==questions[0].id).all()
        self.assertEqual(1, answers[0].id)
        self.assertEqual(2, answers[1].id)
        self.assertEqual("1", answers[0].answer)
        self.assertEqual("2", answers[1].answer)
        self.assertFalse(answers[0].correct)
        self.assertTrue(answers[1].correct)
        answers = self.session.query(Answer).filter(
                                    Answer.question_id==questions[1].id).all()
        self.assertEqual(3, answers[0].id)
        self.assertEqual(4, answers[1].id)
        self.assertEqual(5, answers[2].id)
        self.assertEqual("-1", answers[0].answer)
        self.assertEqual("1", answers[1].answer)
        self.assertEqual("2", answers[2].answer)
        self.assertTrue(answers[0].correct)
        self.assertTrue(answers[1].correct)
        self.assertFalse(answers[2].correct)
        answers = self.session.query(Answer).filter(
                                    Answer.question_id==questions[2].id).all()
        self.assertEqual(0, len(answers))

"""
class ViewAddQuestions(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_add_questions(self):
        from views import view_add_questions
        _populateDB(self.session)
        request = testing.DummyRequest({'id': 1})
        info = view_add_questions(request)
        self.assertTrue("form" in info.keys())
        request = testing.DummyRequest(_createFormData(addQuestionsData))
        request.GET['id'] = 1
        info = view_add_questions(request)
        questions = self.session.query(Question).filter(
                                    Question.test_id==1).all()
        self.assertEquals(6, len(questions))
        self.assertEqual("multipleChoice", questions[3].question_type)
        self.assertEqual("selectTrue", questions[4].question_type)
        self.assertEqual("shortAnswer", questions[5].question_type)
        self.assertEqual('2+2 = ?', questions[3].question)
        self.assertEqual('X^2 = 4', questions[4].question)
        self.assertEqual("Who are you?", questions[5].question)
        self.assertEqual(4, questions[3].id)
        self.assertEqual(5, questions[4].id)
        self.assertEqual(6, questions[5].id)
        answers = self.session.query(Answer).filter(
                                    Answer.question_id==questions[3].id).all()
        self.assertEqual(13, answers[0].id)
        self.assertEqual(14, answers[1].id)
        self.assertEqual("3", answers[0].answer)
        self.assertEqual("4", answers[1].answer)
        self.assertFalse(answers[0].correct)
        self.assertTrue(answers[1].correct)
        answers = self.session.query(Answer).filter(
                                    Answer.question_id==questions[4].id).all()
        self.assertEqual(15, answers[0].id)
        self.assertEqual(16, answers[1].id)
        self.assertEqual(17, answers[2].id)
        self.assertEqual("-2", answers[0].answer)
        self.assertEqual("2", answers[1].answer)
        self.assertEqual("3", answers[2].answer)
        self.assertTrue(answers[0].correct)
        self.assertTrue(answers[1].correct)
        self.assertFalse(answers[2].correct)
        answers = self.session.query(Answer).filter(
                                    Answer.question_id==questions[5].id).all()
        self.assertEqual(0, len(answers))
        

class ViewEditQuestion(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_edit_question(self):
        from views import view_edit_question
        _populateDB(self.session)

        ###test editing multiple choice questions###
        request = testing.DummyRequest({'id': 1,
                                        'question': 1})
        info = view_edit_question(request)
        self.assertEqual(["test", "question", "form"], info.keys())
        self.assertEqual(1, info['test'].id)
        self.assertEqual(1, info['question'].id)
        question = self.session.query(Question).filter(
                                    Question.id == 1).first()
        self.assertEqual("1+1 = ?", question.question)
        self.assertEqual("multipleChoice", question.question_type)
        answers = self.session.query(Answer).filter(
                            Answer.question_id == info['question'].id).all()
        self.assertEqual(6, len(answers))
        request = testing.DummyRequest(_createFormData(editMultipleChoiceData))
        request.GET['id'] = 1
        info = view_edit_question(request)
        self.assertEqual('/edit_test?id=1', info.location)
        question = self.session.query(Question).filter(
                                    Question.id == 1).first()
        self.assertEqual("X^2 = 4", question.question)
        self.assertEqual("selectTrue", question.question_type)
        answers = self.session.query(Answer).filter(
                                    Answer.question_id == 1).all()
        self.assertEqual(4, len(answers))
        self.assertEqual('X = -2',answers[0].answer)
        self.assertEqual('X = 2',answers[1].answer)
        self.assertEqual('X = 3',answers[2].answer)
        self.assertEqual('X = 4',answers[3].answer)
        self.assertTrue(answers[0].correct)
        self.assertTrue(answers[1].correct)
        self.assertFalse(answers[2].correct)
        self.assertFalse(answers[3].correct)

        ###test editing select true question###
        request = testing.DummyRequest({'id': 1,
                                        'question': 2})
        info = view_edit_question(request)
        self.assertEqual(["test", "question", "form"], info.keys())
        self.assertEqual(1, info['test'].id)
        self.assertEqual(2, info['question'].id)
        question = self.session.query(Question).filter(
                                    Question.id == 2).first()
        self.assertEqual("X^2 = 1", question.question)
        self.assertEqual("selectTrue", question.question_type)
        answers = self.session.query(Answer).filter(
                            Answer.question_id == info['question'].id).all()
        self.assertEqual(6, len(answers))
        request = testing.DummyRequest(_createFormData(editSelectTrueData))
        request.GET['id'] = 1
        request.GET['question'] = 2
        info = view_edit_question(request)
        self.assertEqual('/edit_test?id=1', info.location)
        question = self.session.query(Question).filter(
                                    Question.id == 2).first()
        self.assertEqual("1+1=?", question.question)
        self.assertEqual("multipleChoice", question.question_type)
        answers = self.session.query(Answer).filter(
                                    Answer.question_id == 2).all()
        self.assertEqual(4, len(answers))
        self.assertEqual('1',answers[0].answer)
        self.assertEqual('2',answers[1].answer)
        self.assertEqual('3',answers[2].answer)
        self.assertEqual('4',answers[3].answer)
        self.assertFalse(answers[0].correct)
        self.assertTrue(answers[1].correct)
        self.assertFalse(answers[2].correct)
        self.assertFalse(answers[3].correct)

        ###test editing short answer question###
        request = testing.DummyRequest({'id': 1,
                                        'question': 3})
        info = view_edit_question(request)
        self.assertEqual(["test", "question", "form"], info.keys())
        self.assertEqual(1, info['test'].id)
        self.assertEqual(3, info['question'].id)
        question = self.session.query(Question).filter(
                                    Question.id == 3).first()
        self.assertEqual("What is you're name?", question.question)
        request = testing.DummyRequest(_createFormData(editShortAnswerData))
        request.GET['id'] = 1
        request.GET['question'] = 3
        info = view_edit_question(request)
        self.assertEqual('/edit_test?id=1', info.location)
        question = self.session.query(Question).filter(
                                    Question.id == 3).first()
        self.assertEqual("Who are you?", question.question)

        ###test removeing a question###
        questions = self.session.query(Question).filter(
                                       Question.test_id == 1).all()
        self.assertEqual(3, len(questions))
        request = testing.DummyRequest(_createFormData(editRemoveQuestionData))
        request.GET['id'] = 1
        request.GET['question'] = 1
        info = view_edit_question(request)
        self.assertEqual('/edit_test?id=1', info.location)
        questions = self.session.query(Question).filter(
                                       Question.test_id == 1).all()
        self.assertEqual(2, len(questions))
        self.assertEqual(1, questions[0].question_num)
        self.assertEqual(2, questions[1].question_num)

        
        
class ViewDeleteTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_delete_test(self):
        from views import view_delete_test
        _populateDB(self.session)

        request = testing.DummyRequest({})
        request.GET['id'] = 1
        info = view_delete_test(request)
        self.assertTrue('form' in info)
        self.assertEqual("Are you sure you want to delete this test?", 
                         info['message'][0])
        self.assertEqual("Test: Math Test", info['message'][1])
        self.assertEqual("Course: Math 101", info['message'][2])
        request = testing.DummyRequest({})
        requespyramid unit testingt.GET['id'] = 1
        request.GET['no'] = 1
        info = view_delete_test(request)
        self.assertEqual("/edit_test?id=1",info.location)
        request = testing.DummyRequest({})
        request.GET['id'] = 1
        request.GET['yes'] = 1
        info = view_delete_test(request)
        tests = self.session.query(Test).filter(Test.id==1).all()
        questions = self.session.query(Question).filter(
                                        Question.test_id==1).all()
        answers = self.session.query(Answer).filter(
                                        Answer.question_id<=3).all()
        self.assertEqual(0, len(tests))
        self.assertEqual(0, len(questions))
        self.assertEqual(0, len(answers))
        self.assertEqual('/', info.location)


class ViewEditTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_edit_test(self):
        from views import view_edit_test
        _populateDB(self.session)

        request = testing.DummyRequest({})
        request.GET['id'] = 1
        info = view_edit_test(request)
        test = self.session.query(Test).filter(Test.id == 1).first()
        self.assertEqual(test, info['test'])
        self.assertEqual('question 1', info['questions'][0][0])
        self.assertEqual("/edit_question?id=1;question=1",
                        info['questions'][0][1])
        self.assertEqual('question 2', info['questions'][1][0])
        self.assertEqual("/edit_question?id=1;question=2",
                        info['questions'][1][1])
        self.assertEqual('question 3', info['questions'][2][0])
        self.assertEqual("/edit_question?id=1;question=3",
                        info['questions'][2][1])        
        self.assertEqual("/delete_test?id=1",info['delete_link'])
        self.assertEqual("/add_questions?id=1",info['add_link'])

class ViewChooseTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_choose_test(self):
        from views import view_choose_test
        _populateDB(self.session)

        request = testing.DummyRequest({})
        info = view_choose_test(request)
        tests = self.session.query(Test).all()
        self.assertEqual("Math 101", info['tests'][0].course)
        self.assertEqual("Math 102", info['tests'][1].course)
        self.assertEqual("edit_test?id=1", info['tests'][0].url)
        self.assertEqual("edit_test?id=2", info['tests'][1].url)


class ViewIndex(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_index(self):
        from views import view_index
        request = testing.DummyRequest()
        request.session['current_test'] = {}
        self.assertTrue('current_test' in request.session.keys())
        info = view_index(request)
        self.assertTrue('current_test' not in request.session.keys())
        self.assertEqual(info['project'], 'pyquiz')
        test1 = Test("Math Test", "Math 101")
        self.session.add(test1)
        self.session.flush()
        info = view_index(request)
        self.assertEqual(1, len(info['tests']))
        self.assertEqual("Math Test", info['tests'][0].name)
        self.assertEqual("Math 101", info['tests'][0].course)
        self.assertEqual(1, info['tests'][0].id)
        test2 = Test("CS Test", "CS 101")
        self.session.add(test2)
        self.session.flush()
        info = view_index(request)
        self.assertEqual(2, len(info['tests']))
        self.assertEqual(2, info['tests'][1].id)



class ViewQuestion(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_choose_test(self):
        from views import view_question
        _populateDB(self.session)

        request = testing.DummyRequest({'id': 1,
                                        'question': 1})
        info = view_question(request)
        test = self.session.query(Test).filter(Test.id == 1).first()
        self.assertEqual(test, info['test'])
        self.assertTrue('form' in info)
        self.assertEqual('/test?id=1', info['link'])

        request = testing.DummyRequest({'id': 1,
                                        'question': 2})
        info = view_question(request)
        test = self.session.query(Test).filter(Test.id == 1).first()
        self.assertEqual(test, info['test'])
        self.assertTrue('form' in info)
        self.assertEqual('/test?id=1', info['link'])

        request = testing.DummyRequest({'id': 1,
                                        'question': 3})
        info = view_question(request)
        test = self.session.query(Test).filter(Test.id == 1).first()
        self.assertEqual(test, info['test'])
        self.assertTrue('form' in info)
        self.assertEqual('/test?id=1', info['link'])
     
        ###Answer Multiple Choice Question###
        request = testing.DummyRequest(
                          _createFormData(answerMultipleChoiceData))
        request.GET['id'] = 1
        request.session["current_test"] = {"name": "Math Test",
                                           "1": "2"}
        info = view_question(request)
        self.assertEqual('/question?id=1;question=2', info.location)
        self.assertEqual('2', request.session['current_test']['1'])
        
        ###Answer Select True Question###
        request = testing.DummyRequest(_createFormData(answerSelectTrueData))
        request.GET['id'] = 1
        request.GET['question'] = 2
        info = view_question(request)
        self.assertEqual('/question?id=1;question=3', info.location)
        self.assertEqual(['7', '8'], request.session['current_test']['2'])

        ###Answer Short Answer Quesiton
        request = testing.DummyRequest(_createFormData(answerShortAnswerData))
        request.GET['id'] = 1
        request.GET['question'] = 3
        info = view_question(request)
        self.assertEqual('/test?id=1', info.location)
        self.assertEqual("James Boisture",
                        request.session['current_test']['3'])

class ViewTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_test(self):
        from views import view_test
        _populateDB(self.session)
        request = testing.DummyRequest({'id': 1})
        info = view_test(request)
        self.assertTrue("current_test" in request.session)
        request.session["current_test"] = {'name':'Math 101',
                                           '1':'2', '2':'na'}
        info = view_test(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("/grade?id=1", info['link'])
        self.assertEqual("question 1: Answered", info['questions'][0][0])
        self.assertEqual("question 2: NOT ANSWERED", info['questions'][1][0])
        self.assertEqual("question 3: NOT ANSWERED", info['questions'][2][0])
        self.assertEqual("/question?id=1;question=1", info['questions'][0][1])
        self.assertEqual("/question?id=1;question=2", info['questions'][1][1])
        self.assertEqual("/question?id=1;question=3", info['questions'][2][1])

class ViewGradeTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_test(self):
        from views import view_grade_test
        _populateDB(self.session)
        request = testing.DummyRequest({'id': 1})
        info = view_grade_test(request)
        self.assertEqual("/test?id=1", info.location)
        request.session["current_test"] = {'name':'Math Test',
                                           '1':'2', '2':['7','8'],
                                           '3':'James Boisture'}
        info = view_grade_test(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("You got 2 out of 2 correct.(100.0%)",
                         info['message'])
        self.assertEqual('1. Correct', info['questions'][0])
        self.assertEqual('2. Correct', info['questions'][1])
        self.assertEqual('3. Not Graded', info['questions'][2])

        request.session["current_test"] = {'name':'Math Test',
                                           '2':['3','8'],
                                           '3':'James Boisture'}
        info = view_grade_test(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("You got 0 out of 2 correct.(0.0%)",
                         info['message'])
        self.assertEqual('1. INCORRECT', info['questions'][0])
        self.assertEqual('2. INCORRECT', info['questions'][1])
        self.assertEqual('3. Not Graded', info['questions'][2])

        request.session["current_test"] = {'name':'Math Test',
                                           '1': '1',
                                           '3':'James Boisture'}
        info = view_grade_test(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("You got 0 out of 2 correct.(0.0%)",
                         info['message'])
        self.assertEqual('1. INCORRECT', info['questions'][0])
        self.assertEqual('2. INCORRECT', info['questions'][1])
        self.assertEqual('3. Not Graded', info['questions'][2])

        request.session["current_test"] = {'name':'Math Test',
                                           '1': '2',
                                           '2':['7'],
                                           '3':'James Boisture'}
        info = view_grade_test(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("You got 1 out of 2 correct.(50.0%)",
                         info['message'])
        self.assertEqual('1. Correct', info['questions'][0])
        self.assertEqual('2. INCORRECT', info['questions'][1])
        self.assertEqual('3. Not Graded', info['questions'][2])



        question = Question(False, "shortAnswer", "What is you're name?", 
                                                                    2, 1)
        self.session.add(question)
        self.session.flush()
        request = testing.DummyRequest({'id': 2})
        request.session["current_test"] = {'name':'Math Test 2',
                                           '1':'James Boisture'}
        info = view_grade_test(request)
        self.assertEqual(2, info['test'].id)
        self.assertEqual("There were no graded questions.", info['message'])
        self.assertEqual("1. Not Graded", info['questions'][0])
        answers = self.session.query(Answer).filter(
                                     Answer.question_id == question.id).all()
        self.assertEqual(1, len(answers))
        self.assertEqual("username*:James Boisture", answers[0].answer)
"""


