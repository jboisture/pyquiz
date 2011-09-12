"""
tests are currently FIXED.
"""
import unittest
from pyramid import testing

from models import TakenTest, Test, Section, Question, TakenAnswer, Answer, initialize_sql
from webob.multidict import MultiDict

from pyramid.httpexceptions import HTTPFound

from login import *
from testingData import *

from pyramid.security import authenticated_userid
import datetime

def _initTestingDB():
    from models import DBSession
    from models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://')
    return initialize_sql(engine)

def _clearTestingDB(session):
    from models import TakenTest, Section, Test, Question, Answer
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
    takentests = session.query(TakenTest).all()
    for takentest in takentests:
        session.delete(takentest)
        session.flush()
    sections = session.query(Section).all()
    for section in sections:
        session.delete(section)
        session.flush()
    takenanswers = session.query(TakenAnswer).all()
    #for takenanswer in takenanswers:
    #    session.delete(takenanswer)
    #    session.flush()

def _createFormData(data):
    POST = MultiDict()
    for d in data:
        POST.add(d[0], d[1])
    return POST

def _populateDB(session):
    test = Test("Math Test", 1,datetime.date.today(),datetime.date.today()+datetime.timedelta(days=2),5000,'assignment',1)
    session.add(test)
    session.flush()
    test2 = Test("Math Test 2", 1,datetime.date.today(),datetime.date.today() + datetime.timedelta(days=2),5000,'assignment',2)
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
    section = Section(1,1,"Math 101", "teacher'%&teacherII")
    session.add(section)
    session.flush()

def _addSectionDB(session):
    section = Section(1,1,"Math 101", "teacher")
    session.add(section)
    session.flush()


class ViewCreateTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUT(self, formData):
        _addSectionDB(self.session)
        request = testing.DummyRequest(_createFormData(formData))
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        request.GET['id']=1
        from views import view_create_test
        return view_create_test(request)

    def test_view_create(self):
        info = self._callFUT("")
        self.assertTrue('form' in info.keys())

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=False)
        from views import view_create_test
        info = view_create_test(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'student', 'roles': ['student']}}
        request.GET['id'] = 1
        info = view_create_test(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))


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
        self.assertEqual(u'1',test.section)
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
        self.assertEqual(u'1',test.section)
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
        self.assertEqual(u'1',test.section)
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
        self.assertEqual(u'1',test.section)
        _clearTestingDB(self.session)


class ViewAddQuestions(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUT(self, formData):
        _populateDB(self.session)
        request = testing.DummyRequest(_createFormData(formData))
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        request.GET['id']=1
        from views import view_add_questions
        return view_add_questions(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=False)
        from views import view_add_questions
        info = view_add_questions(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'student', 'roles': ['student']}}
        request.GET['id'] = 1
        info = view_add_questions(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_add_questions(self):
        info = self._callFUT("")
        self.assertTrue("form" in info.keys())

    def test_add_questions(self):
        info = self._callFUT(addQuestionsData)
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

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_edit_question
        return view_edit_question(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=False)
        from views import view_edit_question
        info = view_edit_question(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'student', 'roles': ['student']}}
        request.GET['id'] = 1
        info = view_edit_question(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))
        self.assertEqual(info.location,'/')


    def test_view_edit_question(self):

        ###test editing multiple choice questions###
        request = testing.DummyRequest({'id': 1,
                                        'question': 1})
        info = self._callFUT(request)
        self.assertEqual(["test", "main", "question", "form"], info.keys())
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
        info = self._callFUT(request)
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

    def test_edit_select_true(self):
        ###test editing select true question###
        request = testing.DummyRequest({'id': 1,
                                        'question': 2})
        info = self._callFUT(request)
        self.assertEqual(["test", "main", "question", "form"], info.keys())
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
        info = self._callFUT(request)
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

    def test_edit_short_answer(self):
        ###test editing short answer question###
        request = testing.DummyRequest({'id': 1,
                                        'question': 3})
        info = self._callFUT(request)
        self.assertEqual(["test", "main", "question", "form"], info.keys())
        self.assertEqual(1, info['test'].id)
        self.assertEqual(3, info['question'].id)
        question = self.session.query(Question).filter(
                                    Question.id == 3).first()
        self.assertEqual("What is you're name?", question.question)
        request = testing.DummyRequest(_createFormData(editShortAnswerData))
        request.GET['id'] = 1
        request.GET['question'] = 3
        info = self._callFUT(request)
        self.assertEqual('/edit_test?id=1', info.location)
        question = self.session.query(Question).filter(
                                    Question.id == 3).first()
        self.assertEqual("Who are you?", question.question)

    def test_remove_question(self):
        ###test removing a question###
        _populateDB(self.session)
        questions = self.session.query(Question).filter(
                                       Question.test_id == 1).all()
        self.assertEqual(3, len(questions))
        request = testing.DummyRequest(_createFormData(editRemoveQuestionData))
        request.GET['id'] = 1
        request.GET['question'] = 1
        info = self._callFUT(request)
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

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_delete_test
        return view_delete_test(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=False)
        from views import view_delete_test
        info = view_delete_test(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'student', 'roles': ['student']}}
        request.GET['id'] = 1
        info = view_delete_test(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_delete_test(self):
        request = testing.DummyRequest({})
        request.GET['id'] = 1
        info = self._callFUT(request)
        self.assertTrue('form' in info)
        self.assertEqual("Are you sure you want to delete this test?",
                         info['message'][0])
        self.assertEqual("Test: Math Test", info['message'][1])
        self.assertEqual("Section: Math 101", info['message'][2])
        request = testing.DummyRequest({})
        request.GET['id'] = 1
        request.GET['no'] = 1
        info = self._callFUT(request)
        self.assertEqual("/edit_test?id=1",info.location)
        request = testing.DummyRequest({})
        request.GET['id'] = 1
        request.GET['yes'] = 1
        info = self._callFUT(request)
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

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_edit_test
        return view_edit_test(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=False)
        from views import view_edit_test
        info = view_edit_test(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'student', 'roles': ['student']}}
        request.GET['id'] = 1
        info = view_edit_test(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))


    def test_view_edit_test(self):
        request = testing.DummyRequest({})
        request.GET['id'] = 1
        info = self._callFUT(request)
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
"""
class ViewChooseTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_choose_test
        return view_choose_test(request)

    def test_view_choose_test(self):
        request = testing.DummyRequest({})
        info = self._callFUT(request)
        tests = self.session.query(Test).all()
        self.assertEqual("Math 101", info['tests'][0].section)
        self.assertEqual("Math 102", info['tests'][1].section)
        self.assertEqual("edit_test?id=1", info['tests'][0].url)
        self.assertEqual("edit_test?id=2", info['tests'][1].url)

"""


class ViewIndex(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        from views import view_index
        return view_index(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=False)
        from views import view_index
        info = view_index(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_index(self):
        request = testing.DummyRequest()
        request.session['current_test'] = {}
        self.assertTrue('current_test' in request.session.keys())
        info = self._callFUT(request)
        self.assertTrue('current_test' not in request.session.keys())
        self.assertEqual(info['messages'], ['Welcome teacher to pyquiz.', 'You are currently teaching the following classes:', ''])
        info = self._callFUT(request)
        self.assertEqual(1, len(info['sections']))
        self.assertEqual("Math 101", info['sections'][0].section_name)
        self.assertEqual("1", info['sections'][0].section_id)
        self.assertEqual("1", info['sections'][0].term_id)
        self.assertEqual("teacher'%&teacherII", info['sections'][0].instructor)

    def test_view_as_student(self):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='student',permissive=True)
        request = testing.DummyRequest()
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'student', 'roles': ['student']}}
        request.GET['id'] = 1
        from views import view_index
        info = view_index(request)
        self.assertEqual(info['messages'], ['Welcome student to pyquiz.', 'You are currently enrolled in the following classes:', ''])
        self.assertEqual(1, len(info['sections']))
        self.assertEqual("Math 101", info['sections'][0].section_name)
        self.assertEqual("1", info['sections'][0].section_id)
        self.assertEqual("1", info['sections'][0].term_id)
        self.assertEqual("teacher'%&teacherII", info['sections'][0].instructor)


class ViewQuestion(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        from views import view_question
        return view_question(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=True)
        from views import view_question
        info = view_question(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_too_early(self):
        request = testing.DummyRequest(_createFormData(tooEarlyData))
        request.GET["id"]=1
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_create_test
        view_create_test(request)
        request = testing.DummyRequest({'id': 3,
                                        'question': 1})
        info = self._callFUT(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_too_late(self):
        request = testing.DummyRequest(_createFormData(tooLateData))
        request.GET["id"]=1
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_create_test

        view_create_test(request)
        request = testing.DummyRequest({'id': 3,
                                        'question': 1})
        info = self._callFUT(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_no_attempts(self):
        request = testing.DummyRequest(_createFormData(noAttemptsData))
        request.GET["id"]=1
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_create_test
        view_create_test(request)
        request = testing.DummyRequest({'id': 3,
                                        'question': 1})
        info = self._callFUT(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_choose_test(self):
        request = testing.DummyRequest({'id': 1,
                                        'question': 1})
        info = self._callFUT(request)
        test = self.session.query(Test).filter(Test.id == 1).first()
        self.assertEqual(test, info['test'])
        self.assertTrue('form' in info)
        self.assertEqual('/test?id=1', info['link'])

        request = testing.DummyRequest({'id': 1,
                                        'question': 2})
        info = self._callFUT(request)
        test = self.session.query(Test).filter(Test.id == 1).first()
        self.assertEqual(test, info['test'])
        self.assertTrue('form' in info)
        self.assertEqual('/test?id=1', info['link'])

        request = testing.DummyRequest({'id': 1,
                                        'question': 3})
        info = self._callFUT(request)
        test = self.session.query(Test).filter(Test.id == 1).first()
        self.assertEqual(test, info['test'])
        self.assertTrue('form' in info)
        self.assertEqual('/test?id=1', info['link'])

    def test_answer_multiple_choice(self):
        ###Answer Multiple Choice Question###
        request = testing.DummyRequest(
                          _createFormData(answerMultipleChoiceData))
        request.GET['id'] = 1
        request.session["current_test"] = {"name": "Math Test",
                                           "1": "2",}
        info = self._callFUT(request)
        self.assertEqual('/question?id=1;question=2', info.location)
        self.assertEqual('2', request.session['current_test']['1'])

    def test_answer_select_true(self):
        ###Answer Select True Question###
        request = testing.DummyRequest(_createFormData(answerSelectTrueData))
        request.GET['id'] = 1
        request.GET['question'] = 2
        info = self._callFUT(request)
        self.assertEqual('/question?id=1;question=3', info.location)
        self.assertEqual(['7', '8'], request.session['current_test']['2'])

    def test_answer_short_answer(self):
        ###Answer Short Answer Quesiton
        request = testing.DummyRequest(_createFormData(answerShortAnswerData))
        request.GET['id'] = 1
        request.GET['question'] = 3
        info = self._callFUT(request)
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

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        from views import view_test
        return view_test(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=True)
        from views import view_test
        info = view_test(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_too_early(self):
        request = testing.DummyRequest(_createFormData(tooEarlyData))
        request.GET["id"]=1
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_create_test
        view_create_test(request)
        request = testing.DummyRequest({'id': 3,
                                        'question': 1})
        info = self._callFUT(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_too_late(self):
        request = testing.DummyRequest(_createFormData(tooLateData))
        request.GET["id"]=1
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_create_test
        view_create_test(request)
        request = testing.DummyRequest({'id': 3,
                                        'question': 1})
        info = self._callFUT(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_no_attempts(self):
        request = testing.DummyRequest(_createFormData(noAttemptsData))
        request.GET["id"]=1
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}}
        from views import view_create_test
        view_create_test(request)
        request = testing.DummyRequest({'id': 3,
                                        'question': 1})
        info = self._callFUT(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))


    def test_view_test(self):
        request = testing.DummyRequest({'id': 1})
        info = self._callFUT(request)
        self.assertTrue("current_test"  in request.session)
        request.session["current_test"] = {'name':'Math 101',
                                           '1':'2', '2':'na'}
        info = self._callFUT(request)
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

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        from views import view_grade_test
        return view_grade_test(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=True)
        from views import view_grade_test
        info = view_grade_test(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_test(self):
        request = testing.DummyRequest({'id': 1})
        info = self._callFUT(request)
        self.assertEqual("/test?id=1", info.location)
        request.session["current_test"] = {'name':'Math Test',
                                           '1':'2', '2':['7','8'],
                                           '3':'James Boisture'}
        info = self._callFUT(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("You got 2 out of 2 correct(100.0%). This grade only includes automaticly graded questions.",
                         info['message'])
        self.assertEqual('1. Correct', info['questions'][0])
        self.assertEqual('2. Correct', info['questions'][1])
        self.assertEqual('3. Waiting for teacher to grade.', info['questions'][2])

        request.session["current_test"] = {'name':'Math Test',
                                           '2':['3','8'],
                                           '3':'James Boisture'}
        info = self._callFUT(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("You got 0 out of 2 correct(0.0%). This grade only includes automaticly graded questions.",
                         info['message'])
        self.assertEqual('1. INCORRECT', info['questions'][0])
        self.assertEqual('2. INCORRECT', info['questions'][1])
        self.assertEqual('3. Waiting for teacher to grade.', info['questions'][2])

        request.session["current_test"] = {'name':'Math Test',
                                           '1': '1',
                                           '3':'James Boisture'}
        info = self._callFUT(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("You got 0 out of 2 correct(0.0%). This grade only includes automaticly graded questions.",
                         info['message'])
        self.assertEqual('1. INCORRECT', info['questions'][0])
        self.assertEqual('2. INCORRECT', info['questions'][1])
        self.assertEqual('3. Waiting for teacher to grade.', info['questions'][2])

        request.session["current_test"] = {'name':'Math Test',
                                           '1': '2',
                                           '2':['7'],
                                           '3':'James Boisture'}
        info = self._callFUT(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("You got 1 out of 2 correct(50.0%). This grade only includes automaticly graded questions.",
                         info['message'])
        self.assertEqual('1. Correct', info['questions'][0])
        self.assertEqual('2. INCORRECT', info['questions'][1])
        self.assertEqual('3. Waiting for teacher to grade.', info['questions'][2])



        question = Question(False, "shortAnswer", "What is you're name?",
                                                                    2, 1)
        self.session.add(question)
        self.session.flush()
        request = testing.DummyRequest({'id': 2})
        request.session["current_test"] = {'name':'Math Test 2',
                                           '1':'James Boisture'}
        info = self._callFUT(request)
        self.assertEqual(2, info['test'].id)
        self.assertEqual("There were no graded questions.", info['message'])
        self.assertEqual("1. Waiting for teacher to grade.", info['questions'][0])
        answers = self.session.query(Answer).filter(
                                     Answer.question_id == question.id).all()
        self.assertEqual(1, len(answers))
        self.assertEqual("username*:James Boisture", answers[0].answer)


        request = testing.DummyRequest({'id': 1})
        request.session["current_test"] = {'name':'Math Test',
                                           '1': '2',
                                           '2':[],
                                           '3':'James Boisture'}
        info = self._callFUT(request)
        self.assertEqual(1, info['test'].id)
        self.assertEqual("You got 1 out of 2 correct(50.0%). This grade only includes automaticly graded questions.",
                         info['message'])
        self.assertEqual('1. Correct', info['questions'][0])
        self.assertEqual('2. INCORRECT', info['questions'][1])
        self.assertEqual('3. Waiting for teacher to grade.', info['questions'][2])

        request = testing.DummyRequest({'id': 1})
        request.session["current_test"] = {'name':'Math Test',
                                           '1': '2',
                                           '2':[],
                                           '3':'James Boisture'}
    def test_has_been_graded(self):
        _populateDB(self.session)
        dbsession = DBSession()
        test = Test("Test Test", 1,datetime.date.today(),datetime.date.today()+datetime.timedelta(days=2),5000,'assignment',1)
        self.session.add(test)
        self.session.flush()
        question = Question(True, "multipleChoice", "1+1 = ?", test.id, 3)
        self.session.add(question)
        self.session.flush()
        answer = Answer(question.id, "2", True)
        self.session.add(answer)
        self.session.flush()
        takentest = TakenTest(1, 'teacher', 'teacher', 3, 3, False,1)
        self.session.add(takentest)
        self.session.flush()
        takenanswer = TakenAnswer(1, question, '2', True, True)
        self.session.add(takenanswer)
        self.session.flush()
        request = testing.DummyRequest({'id': 1})
        request.session["current_test"] = {'name':'Test Test',
                                           '1': '2'}
        info = self._callFUT(request)

class ViewUngradedTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        from views import view_ungraded_tests
        return view_ungraded_tests(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=True)
        from views import view_ungraded_tests
        info = view_ungraded_tests(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_ungraded_tests(self):
        request = testing.DummyRequest({'id':1})
        test1 = TakenTest(1, 'student', 'student', 3, 3, False,1)
        self.session.add(test1)
        self.session.flush()
        info = self._callFUT(request)
        self.assertEqual(info['message'], 'There are no tests to grade')
        test2 = TakenTest(1, 'student', 'student', 0, 0, True,1)
        self.session.add(test2)
        self.session.flush()
        info = self._callFUT(request)
        self.assertEqual(info['test'].name, 'Math Test')
        self.assertEqual(info['taken_tests'],[test2])
        self.assertEqual(info['message'], '')
        request.session['current_test']="I am a test"
        info = self._callFUT(request)
        self.assertTrue("current_test" not in request.session)


class ViewGradeQuestion(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        request.GET['id'] = 1
        from views import view_grade_question
        return view_grade_question(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=True)
        from views import view_grade_question
        info = view_grade_question(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_grade_question(self):
        dbsession = DBSession()
        _populateDB(self.session)
        request = testing.DummyRequest({'id':1})
        test1 = TakenTest(1, 'student', 'student', 2, 2, False,1)
        self.session.add(test1)
        self.session.flush()
        question1 = dbsession.query(Question).first()
        takenquestion = TakenAnswer(1, question1, '2', False, False)
        self.session.add(takenquestion)
        self.session.flush()
        info = self._callFUT(request)
        self.assertEqual(len(info['message']), 3)
        self.assertEqual(info['message'][0], "Question Number 1")
        self.assertEqual(info['message'][1], "Question: 1+1 = ?")
        self.assertEqual(info['message'][2], "student's answer: 2")

    def test_grade_correct_question(self):
        dbsession = DBSession()
        _populateDB(self.session)
        request = testing.DummyRequest({'id':1})
        request.POST = {'correct':True}
        test1 = TakenTest(1, 'student', 'student', 2, 2, False,1)
        self.session.add(test1)
        self.session.flush()
        question1 = dbsession.query(Question).first()
        takenquestion = TakenAnswer(1, question1, '3', False, False)
        self.session.add(takenquestion)
        self.session.flush()
        info = self._callFUT(request)
        self.assertTrue(type(info), type(HTTPFound()))
        self.assertEqual(test1.correct_graded_questions,3)

    def test_grade_incorrect_question(self):
        dbsession = DBSession()
        _populateDB(self.session)
        request = testing.DummyRequest({'id':1})
        request.POST = {'incorrect':True}
        test1 = TakenTest(1, 'student', 'student', 1, 1, False,1)
        self.session.add(test1)
        self.session.flush()
        question1 = dbsession.query(Question).first()
        takenquestion = TakenAnswer(1, question1, '2', True, True)
        self.session.add(takenquestion)
        self.session.flush()
        request.session['current_test']="I am a test"
        info = self._callFUT(request)
        self.assertTrue(type(info), type(HTTPFound()))
        self.assertEqual(test1.correct_graded_questions,0)


class ViewGradeSubmittedTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        from views import view_grade_submitted_test
        return view_grade_submitted_test(request)

    def test_permission_denied(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='student',permissive=True)
        from views import view_grade_submitted_test
        info = view_grade_submitted_test(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_too_early(self):
        _populateDB(self.session)
        test1 = Test("TooEarlyTest", 1, datetime.datetime.now()+datetime.timedelta(days=20),
                                      datetime.datetime.now()+datetime.timedelta(days=19),
                                      5000, "assignment", 1)
        self.session.add(test1)
        self.session.flush()
        takentest1 = TakenTest(3, 'student', 'student', 2, 2, False,1)
        self.session.add(takentest1)
        self.session.flush()
        request = testing.DummyRequest()
        request.GET["id"]=1
        request.session['current_test']="I am a test"
        info = self._callFUT(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_too_late(self):
        _populateDB(self.session)
        test1 = Test("TooEarlyTest", 1, datetime.datetime.now()-datetime.timedelta(days=20),
                                      datetime.datetime.now()-datetime.timedelta(days=19),
                                      5000, "assignment", 1)
        self.session.add(test1)
        self.session.flush()
        takentest1 = TakenTest(3, 'student', 'student', 2, 2, False,1)
        self.session.add(takentest1)
        self.session.flush()
        request = testing.DummyRequest()
        request.GET["id"]=1
        info = self._callFUT(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_no_attempts(self):
        _populateDB(self.session)
        test1 = Test("TooEarlyTest", 1, datetime.datetime.now(),
                                      datetime.datetime.now()+datetime.timedelta(days=1),
                                      0, "assignment", 1)
        self.session.add(test1)
        self.session.flush()
        takentest1 = TakenTest(3, 'student', 'student', 2, 2, False,1)
        self.session.add(takentest1)
        self.session.flush()
        request = testing.DummyRequest()
        request.GET["id"]=1
        info = self._callFUT(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_grade_submitted_test_ungraded_question(self):
        _populateDB(self.session)
        dbsession = DBSession()
        question1 = dbsession.query(Question).first()
        takenquestion = TakenAnswer(1, question1, '2', False, False)
        self.session.add(takenquestion)
        self.session.flush()
        request = testing.DummyRequest()
        request.GET['id'] = 1
        takentest1 = TakenTest(1, 'student', 'student', 2, 2, False,1)
        self.session.add(takentest1)
        self.session.flush()
        info = self._callFUT(request)
        self.assertEqual(info['messages'][0], 'Test Name: Math Test')
        self.assertEqual(info['answers'][0].html, '<a href="grade_question?id=1">1. Not Graded</a>')

    def test_view_grade_submitted_test_graded_correct(self):
        _populateDB(self.session)
        dbsession = DBSession()
        question1 = dbsession.query(Question).filter(Question.id==2).first()
        takenquestion = TakenAnswer(1, question1, '2', True, True)
        self.session.add(takenquestion)
        self.session.flush()
        request = testing.DummyRequest()
        request.GET['id'] = 1
        takentest1 = TakenTest(1, 'student', 'student', 2, 2, False,1)
        self.session.add(takentest1)
        self.session.flush()
        info = self._callFUT(request)
        self.assertEqual(info['messages'][0], 'Test Name: Math Test')
        self.assertEqual(info['answers'][0].html, '<p>2. Graded: Correct</p>')

    def test_view_grade_submitted_test_graded_incorrect(self):
        _populateDB(self.session)
        dbsession = DBSession()
        question1 = dbsession.query(Question).filter(Question.id==3).first()
        takenquestion = TakenAnswer(1, question1, '1', True, False)
        self.session.add(takenquestion)
        self.session.flush()
        request = testing.DummyRequest()
        request.GET['id'] = 1
        takentest1 = TakenTest(1, 'student', 'student', 2, 2, False,1)
        self.session.add(takentest1)
        self.session.flush()
        info = self._callFUT(request)
        self.assertEqual(info['messages'][0], 'Test Name: Math Test')
        self.assertEqual(info['answers'][0].html, '<p>3. Graded: Incorrect</p>')


class ViewSectionTeacher(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUT(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        from views import view_section_teacher
        return view_section_teacher(request)

    def test_permission_denied(self):
        request = testing.DummyRequest({'id':1})
        self.config.testing_securitypolicy(userid='student',permissive=True)
        from views import view_section_teacher
        info = view_section_teacher(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))
        request.session ={'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'student', 'roles': ['student']}}
        request.GET['id'] = 1
        info = view_section_teacher(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_section_teacher(self):
        oldtest = Test("OldTest", 1, datetime.datetime.now()-datetime.timedelta(days=20),
                                      datetime.datetime.now()-datetime.timedelta(days=19),
                                      5000, "assignment", 1)
        self.session.add(oldtest)
        self.session.flush()
        futuretest = Test("FutureTest", 1, datetime.datetime.now()+datetime.timedelta(days=20),
                                      datetime.datetime.now()+datetime.timedelta(days=19),
                                      5000, "assignment", 1)
        self.session.add(futuretest)
        self.session.flush()
        takentest1 = TakenTest(1, 'student', 'student', 2, 2, True,1)
        self.session.add(takentest1)
        self.session.flush()
        request = testing.DummyRequest({'id':1})
        request.session['current_test']="I am a test"
        info = self._callFUT(request)
        self.assertTrue('current_test' not in request.session)

    def test_view_section_teacher_no_tests(self):
        _addSectionDB(self.session)
        request = testing.DummyRequest({'id':1})
        request.session['current_test']="I am a test"
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        from views import view_section_teacher
        info = view_section_teacher(request)
        self.assertTrue('current_test' not in request.session)


class ViewSection(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def _callFUTTeacher(self, request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        from views import view_section
        return view_section(request)

    def _callFUTStudent(self,request):
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='student',
                                           permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'student', 'roles': ['student']}})
        from views import view_section
        return view_section(request)

    def test_permission_denied(self):
        request = testing.DummyRequest({'id':1})
        self.config.testing_securitypolicy(userid='student',permissive=True)
        from views import view_section
        info = view_section(request)
        self.assertEqual(type(info),type(HTTPFound(location='/')))

    def test_view_section_as_teacher(self):
        request = testing.DummyRequest({'id':1})
        info = self._callFUTTeacher(request)

    def test_view_section_as_student(self):
        oldtest = Test("OldTest", 1, datetime.datetime.now()-datetime.timedelta(days=20),
                                      datetime.datetime.now()-datetime.timedelta(days=19),
                                      5000, "assignment", 1)
        self.session.add(oldtest)
        self.session.flush()
        nowtest = Test("NowTest", 1, datetime.datetime.now()-datetime.timedelta(days=1),
                                      datetime.datetime.now()+datetime.timedelta(days=1),
                                      0, "assignment", 1)
        self.session.add(nowtest)
        self.session.flush()
        futuretest = Test("FutureTest", 1, datetime.datetime.now()+datetime.timedelta(days=20),
                                      datetime.datetime.now()+datetime.timedelta(days=19),
                                      5000, "assignment", 1)
        self.session.add(futuretest)
        self.session.flush()
        request = testing.DummyRequest({'id':1})
        request.session['current_test']="I am a test"
        info = self._callFUTStudent(request)
        self.assertEqual(len(info['current_tests']), 2)
        self.assertEqual(len(info['old_tests']), 2)
        self.assertEqual(len(info['upcoming_tests']), 1)
        self.assertEqual(info['messages'],[u'Section: Math 101', u"Instructor(s): teacher', teacherII", 'There are 5 tests to take:'])


class LoginTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)

    def test_log_in(self):
        request = testing.DummyRequest()
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.params = {'login': u'name', 'password': u'password', 'form.submitted': u'Log In'}
        info = login(request)
        self.assertEqual(request.session, {'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'name', 'roles': ['teacher']}})
        self.assertEqual(type(info), type(HTTPFound()))
        self.assertEqual(info.location, '/index')
        
    def test_log_in_bad_info(self):
        request = testing.DummyRequest()
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.params = {'login': u'name', 'password': u'INCORRECT', 'form.submitted': u'Log In'}
        info = login(request)
        self.assertEqual(request.session, {})
        self.assertEqual(info['message'], 'Failed login')
    
    def test_log_in_noinfo(self):
        request = testing.DummyRequest()
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        info = login(request)
        self.assertEqual(request.session, {})
        self.assertEqual(info['message'], '')
        
    def test_log_in_already_loggedin(self):
        request = testing.DummyRequest()
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='student',
                                           permissive=True)
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'student', 'roles': ['student']}})
        info = login(request)
        self.assertEqual(type(info), type(HTTPFound()))
    
    def test_log_out(self):
        request = testing.DummyRequest()
        _populateDB(self.session)
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.params = {'login': u'name', 'password': u'password', 'form.submitted': u'Log In'}
        request.session.update({'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}})
        info = logout(request)
        self.assertEqual(request.session, {})
        self.assertEqual(type(info), type(HTTPFound()))
        
    def test_schooltool_no_sections(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        userinfo = {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'teacher', 'roles': ['teacher']}
        userinfo = schooltool_login('name','password',userinfo)
        dbsession = DBSession()
        c = dbsession.query(Section).filter(Section.section_id == 1).all()
        self.assertEqual(c[0].section_name,"Math101 (1)")
        self.assertEqual(c[0].instructor,"teacher")
        
    def test_schooltool_no_sections_student(self):
        request = testing.DummyRequest()
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        userinfo = {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'Student', 'roles': []}
        userinfo = schooltool_login('Student','password',userinfo)
        dbsession = DBSession()
        c = dbsession.query(Section).filter(Section.section_id == 1).all()
        self.assertEqual(c[0].section_name,"Math101 (1)")

    def test_log_in_no_instructor(self):
        request = testing.DummyRequest()
        section = Section(1,1,"Math 101", "")
        self.session.add(section)
        self.session.flush()
        self.config.testing_securitypolicy(userid='teacher',
                                          permissive=True)
        request.params = {'login': u'name', 'password': u'password', 'form.submitted': u'Log In'}
        info = login(request)
        self.assertEqual(request.session, {'user': {'sections': [['quarter-one', '1', 'Math101 (1)']], 'first_name': 'Edward', 'last_name': 'Reynolds', 'name': 'name', 'roles': ['teacher']}})


class ZFunctionalTests(unittest.TestCase): #Z so it's called last. wsgi stuff messes up deform. 
    
    teacher_login = '?login=name&password=password' \
                   '&form.submitted=Login'
    student_login = '?login=Student&password=password' \
                   '&form.submitted=Login'
    wrong_login = '?login=name&password=incorrect' \
                   '&form.submitted=Login'
    
    def setUp(self):
        from pyquiz import main
        settings = {'sqlalchemy.url': 'sqlite:///testpyquiz.db'}
        app = main({}, **settings)
        from webtest import TestApp
        self.testapp = TestApp(app)
    
    def tearDown(self):
        del self.testapp
        DBSession.remove()
    
    def test_view_login(self):
        res = self.testapp.get('/',status=200)
        self.assertTrue('Login' in res.body)
        
    def test_404(self):
        self.testapp.get('/IDONTEXIST', status=404)
    
    def test_invalid_login(self):
        res = self.testapp.get(self.wrong_login,status=200)
        self.assertTrue('Failed login' in res.body)
        
    def test_index_anonymous(self):
        res = self.testapp.get('/index?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_index_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/index?id=1', status=200)
        self.assertTrue('Welcome' in res.body)

    def test_index_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/index?id=1', status=200)
        self.assertTrue('Welcome' in res.body)

    def test_create_test_anonymous(self):
        res = self.testapp.get('/create_test?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_create_test_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/create_test?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_create_test_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/create_test?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_grade_submitted_test_anonymous(self):
        res = self.testapp.get('/grade_submitted_test?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_grade_submitted_test_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/grade_submitted_test?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_grade_submitted_test_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/grade_submitted_test?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_grade_question_anonymous(self):
        res = self.testapp.get('/grade_question?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_grade_question_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/grade_question?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_grade_question_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/grade_question?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_ungraded_tests_anonymous(self):
        res = self.testapp.get('/ungraded_tests?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_ungraded_tests_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/ungraded_tests?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_ungraded_tests_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/ungraded_tests?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_question_anonymous(self):
        res = self.testapp.get('/question?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_question_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/question?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_question_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/question?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_test_anonymous(self):
        res = self.testapp.get('/test?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_test_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/test?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_test_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/test?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_section_anonymous(self):
        res = self.testapp.get('/section?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_section_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/section?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_section_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/section?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_section_teacher_anonymous(self):
        res = self.testapp.get('/section_teacher?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_section_teacher_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/section_teacher?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_section_teacher_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/section_teacher?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_grade_anonymous(self):
        res = self.testapp.get('/grade?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_grade_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/grade?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_grade_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/grade?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_edit_test_anonymous(self):
        res = self.testapp.get('/edit_test?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_edit_test_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/edit_test?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_edit_test_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/edit_test?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_edit_question_anonymous(self):
        res = self.testapp.get('/edit_question?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_edit_question_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/edit_question?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_edit_question_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/edit_question?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_delete_test_anonymous(self):
        res = self.testapp.get('/delete_test?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_delete_test_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/delete_test?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_delete_test_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/delete_test?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_add_questions_anonymous(self):
        res = self.testapp.get('/add_questions?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_add_questions_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/add_questions?id=1', status=200)
        self.assertTrue('' in res.body)

    def test_add_questions_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/add_questions?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_logout_anonymous(self):
        res = self.testapp.get('/logout?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_logout_teacher(self):
        self.testapp.get(self.teacher_login, status=302)
        res = self.testapp.get('/logout?id=1', status=302)
        self.assertTrue('' in res.body)

    def test_logout_student(self):
        self.testapp.get(self.student_login, status=302)
        res = self.testapp.get('/logout?id=1', status=302)
        self.assertTrue('' in res.body)




