import unittest

from pyramid import testing
from models import Test, Question, Answer
from webob.multidict import MultiDict

selectTrueData = [('_charset_', u'UTF-8'), ('__formid__', u'deform'), ('name', u'Math Test'), 
                  ('class_id', u'Math 101'), ('__start__', u'questions:sequence'), ('__start__', u'questions:mapping'),
                  ('text', u'1+1 = ?'), ('__start__', u'answers:sequence'), ('__start__', u'answers:mapping'), 
                  ('text', u'1'), ('correct', u'true'), ('__end__', u'answers:mapping'), 
                  ('__start__', u'answers:mapping'), ('text', u'2'), ('correct', u'true'),
                  ('__end__', u'answers:mapping'), ('__end__', u'answers:sequence'), 
                  ('__end__', u'questions:mapping'), ('__end__', u'questions:sequence'), 
                  ('__start__', u'short_answer_questions:sequence'), ('__end__', u'short_answer_questions:sequence'),
                  ('submit', u'submit')]

multipleChoiceData = [('_charset_', u'UTF-8'), ('__formid__', u'deform'), ('name', u'Math Test'), 
                      ('class_id', u'Math 101'), ('__start__', u'questions:sequence'), ('__start__', u'questions:mapping'),
                      ('text', u'1+1 = ?'), ('__start__', u'answers:sequence'), ('__start__', u'answers:mapping'), 
                      ('text', u'1'), ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'), ('text', u'2'), 
                      ('correct', u'true'), ('__end__', u'answers:mapping'), ('__end__', u'answers:sequence'), 
                      ('__end__', u'questions:mapping'), ('__end__', u'questions:sequence'), 
                      ('__start__', u'short_answer_questions:sequence'), ('__end__', u'short_answer_questions:sequence'),
                      ('submit', u'submit')]

shortAnswerData = [('_charset_', u'UTF-8'), ('__formid__', u'deform'),
                   ('name', u'Short Answer'), ('class_id', u'Test'),
                   ('__start__', u'questions:sequence'), ('__end__', u'questions:sequence'),
                   ('__start__', u'short_answer_questions:sequence'), ('__start__', u'questions:mapping'),
                   ('text', u"What is you're name?"), ('__end__', u'questions:mapping'),
                   ('__end__', u'short_answer_questions:sequence'), ('submit', u'submit')]

allTypesData = [('_charset_', u'UTF-8'), ('__formid__', u'deform'), ('name', u'All Types'),
                ('class_id', u'Math 101'), ('__start__', u'questions:sequence'),
                ('__start__', u'questions:mapping'), ('text', u'1+1 = ?'), ('__start__', u'answers:sequence'),
                ('__start__', u'answers:mapping'), ('text', u'1'), ('__end__', u'answers:mapping'),
                ('__start__', u'answers:mapping'), ('text', u'2'), ('correct', u'true'),
                ('__end__', u'answers:mapping'), ('__end__', u'answers:sequence'), ('__end__', u'questions:mapping'),
                ('__start__', u'questions:mapping'), ('text', u'x^2 = 1'), ('__start__', u'answers:sequence'),
                ('__start__', u'answers:mapping'), ('text', u'-1'), ('correct', u'true'),
                ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'), ('text', u'1'), ('correct', u'true'),
                ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'), ('text', u'2'),
                ('__end__', u'answers:mapping'), ('__end__', u'answers:sequence'), ('__end__', u'questions:mapping'),
                ('__end__', u'questions:sequence'), ('__start__', u'short_answer_questions:sequence'),
                ('__start__', u'questions:mapping'), ('text', u"What is you're name?"), ('__end__', u'questions:mapping'),
                ('__end__', u'short_answer_questions:sequence'), ('submit', u'submit')]

addQuestionsData = [('_charset_', u'UTF-8'), ('__formid__', u'deform'), ('__start__', u'questions:sequence'),
                    ('__start__', u'questions:mapping'), ('text', u'2+2 = ?'), ('__start__', u'answers:sequence'),
                    ('__start__', u'answers:mapping'), ('text', u'3'), ('__end__', u'answers:mapping'),
                    ('__start__', u'answers:mapping'), ('text', u'4'), ('correct', u'true'), ('__end__', u'answers:mapping'),
                    ('__end__', u'answers:sequence'), ('__end__', u'questions:mapping'), ('__start__', u'questions:mapping'),
                    ('text', u'X^2 = 4'), ('__start__', u'answers:sequence'), ('__start__', u'answers:mapping'),
                    ('text', u'-2'), ('correct', u'true'), ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'),
                    ('text', u'2'), ('correct', u'true'), ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'),
                    ('text', u'3'), ('__end__', u'answers:mapping'), ('__end__', u'answers:sequence'),
                    ('__end__', u'questions:mapping'), ('__end__', u'questions:sequence'), ('__start__', u'short_answer_questions:sequence'),
                    ('__start__', u'questions:mapping'), ('text', u'Who are you?'), ('__end__', u'questions:mapping'),
                    ('__end__', u'short_answer_questions:sequence'), ('add questions', u'add questions')]

editMultipleChoiceData = [('_charset_', u'UTF-8'), ('__formid__', u'deform'), ('text', u'X^2 = 4'), 
                          ('__star t__', u'answers:sequence'), ('__start__', u'answers:mapping'), ('text', u'1'),
                          ('remove', u'true'), ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'),
                          ('text', u'2'), ('correct', u'true'), ('remove', u'true'), ('__end__', u'answers:mapping'),
                          ('__start__', u'answers:mapping'), ('text', u'X = -2'), ('correct', u'true'), ('__end__', u'answers:mapping'),
                          ('__start__', u'answers:mapping'), ('text', u'4'), ('remove', u'true'), ('__end__', u'answers:mapping'),
                          ('__start__', u'answers:mapping'), ('text', u'X = 2'), ('correct', u'true'), ('__end__', u'answers:mapping'),
                          ('__start__', u'answers:mapping'), ('text', u'6'), ('remove', u'true'), ('__end__', u'answers:mapping'),
                          ('__start__', u'answers:mapping'), ('text', u'X = 3'), ('__end__', u'answers:mapping'),
                          ('__start__', u'answers:mapping'), ('text', u'X = 4'), ('__end__', u'answers:mapping'),
                          ('__end__', u'answers:sequence'), ('submit changes', u'submit changes')]

editSelectTrueData = [('_charset_', u'UTF-8'), ('__formid__', u'deform'), ('text', u'1+1=?'), ('__start_ _', u'answers:sequence'),
                      ('__start__', u'answers:mapping'), ('text', u'1'), ('__end__', u'answers:mapping'),
                      ('__start__', u'answers:mapping'), ('text', u'1'), ('correct', u'true'), ('remove', u'true'),
                      ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'), ('text', u'2'), ('correct', u'true'),
                      ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'), ('text', u'3'),
                      ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'), ('text', u'4'), ('remove', u'true'),
                      ('__end__', u'answers:mapping'), ('__start__', u'answers:mapping'), ('text', u'4'),
                      ('__end__', u'answers:mapping'), ('__end__', u'answers:sequence'), ('submit changes', u'submit changes')]

editShortAnswerData = [('_charset_', u'UTF-8'), ('__formid__', u'deform'), ('text', u'Who are you?'), ('submit changes', u'submit changes')]
editRemoveQuestionData = [('_charset_', u'UTF-8'), ('__formid__', u'deform'), ('text', u'Who are you?'),
                          ('remove', u'true'), ('submit changes', u'submit changes')]

def _initTestingDB():
    from models import DBSession
    from models import Base
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return DBSession

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
    question = Question(True, "shortAnswer", "What is you're name?", test.id, 3)
    session.add(question)
    session.flush()


class ViewCeateTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.session = _initTestingDB()

    def tearDown(self):
        testing.tearDown()
        _clearTestingDB(self.session)


    def test_view_create(self):
        from views import view_create_test
        request = testing.DummyRequest()
        info = view_create_test(request)
        self.assertTrue('form' in info.keys())

        ###Test creating a multipleChoice question with one correct answer###
        request = testing.DummyRequest(_createFormData(multipleChoiceData))
        info = view_create_test(request)
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

        ###Test creating a selectTrue question with more than one correct answer###
        request = testing.DummyRequest(_createFormData(selectTrueData))
        info = view_create_test(request)
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

        ###Test creating a shortAnswer question with more than one correct answer###
        request = testing.DummyRequest(_createFormData(shortAnswerData))
        info = view_create_test(request)
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

        ###Test creating one of each type of question###
        request = testing.DummyRequest(_createFormData(allTypesData))
        info = view_create_test(request)
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
        answers = self.session.query(Answer).filter(Answer.question_id==questions[0].id).all()
        self.assertEqual(1, answers[0].id)
        self.assertEqual(2, answers[1].id)
        self.assertEqual("1", answers[0].answer)
        self.assertEqual("2", answers[1].answer)
        self.assertFalse(answers[0].correct)
        self.assertTrue(answers[1].correct)
        answers = self.session.query(Answer).filter(Answer.question_id==questions[1].id).all()
        self.assertEqual(3, answers[0].id)
        self.assertEqual(4, answers[1].id)
        self.assertEqual(5, answers[2].id)
        self.assertEqual("-1", answers[0].answer)
        self.assertEqual("1", answers[1].answer)
        self.assertEqual("2", answers[2].answer)
        self.assertTrue(answers[0].correct)
        self.assertTrue(answers[1].correct)
        self.assertFalse(answers[2].correct)
        answers = self.session.query(Answer).filter(Answer.question_id==questions[2].id).all()
        self.assertEqual(0, len(answers))

class ViewAddQuestionsTest(unittest.TestCase):

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
        questions = self.session.query(Question).filter(Question.test_id==1).all()
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
        answers = self.session.query(Answer).filter(Answer.question_id==questions[3].id).all()
        self.assertEqual(13, answers[0].id)
        self.assertEqual(14, answers[1].id)
        self.assertEqual("3", answers[0].answer)
        self.assertEqual("4", answers[1].answer)
        self.assertFalse(answers[0].correct)
        self.assertTrue(answers[1].correct)
        answers = self.session.query(Answer).filter(Answer.question_id==questions[4].id).all()
        self.assertEqual(15, answers[0].id)
        self.assertEqual(16, answers[1].id)
        self.assertEqual(17, answers[2].id)
        self.assertEqual("-2", answers[0].answer)
        self.assertEqual("2", answers[1].answer)
        self.assertEqual("3", answers[2].answer)
        self.assertTrue(answers[0].correct)
        self.assertTrue(answers[1].correct)
        self.assertFalse(answers[2].correct)
        answers = self.session.query(Answer).filter(Answer.question_id==questions[5].id).all()
        self.assertEqual(0, len(answers))
        

class ViewEditQuestionTest(unittest.TestCase):

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
        question = self.session.query(Question).filter(Question.id == 1).first()
        self.assertEqual("1+1 = ?", question.question)
        self.assertEqual("multipleChoice", question.question_type)
        answers = self.session.query(Answer).filter(Answer.question_id == info['question'].id).all()
        self.assertEqual(6, len(answers))
        request = testing.DummyRequest(_createFormData(editMultipleChoiceData))
        request.GET['id'] = 1
        request.GET['question'] = 1
        info = view_edit_question(request)
        self.assertEqual('/edit_test?id=1', info.location)
        question = self.session.query(Question).filter(Question.id == 1).first()
        self.assertEqual("X^2 = 4", question.question)
        self.assertEqual("selectTrue", question.question_type)
        answers = self.session.query(Answer).filter(Answer.question_id == 1).all()
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
        question = self.session.query(Question).filter(Question.id == 2).first()
        self.assertEqual("X^2 = 1", question.question)
        self.assertEqual("selectTrue", question.question_type)
        answers = self.session.query(Answer).filter(Answer.question_id == info['question'].id).all()
        self.assertEqual(6, len(answers))
        request = testing.DummyRequest(_createFormData(editSelectTrueData))
        request.GET['id'] = 1
        request.GET['question'] = 2
        info = view_edit_question(request)
        self.assertEqual('/edit_test?id=1', info.location)
        question = self.session.query(Question).filter(Question.id == 2).first()
        self.assertEqual("1+1=?", question.question)
        self.assertEqual("multipleChoice", question.question_type)
        answers = self.session.query(Answer).filter(Answer.question_id == 2).all()
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
        question = self.session.query(Question).filter(Question.id == 3).first()
        self.assertEqual("What is you're name?", question.question)
        request = testing.DummyRequest(_createFormData(editShortAnswerData))
        request.GET['id'] = 1
        request.GET['question'] = 3
        info = view_edit_question(request)
        self.assertEqual('/edit_test?id=1', info.location)
        question = self.session.query(Question).filter(Question.id == 3).first()
        self.assertEqual("Who are you?", question.question)

        ###test removeing a question###
        questions = self.session.query(Question).all()
        self.assertEqual(3, len(questions))
        request = testing.DummyRequest(_createFormData(editRemoveQuestionData))
        request.GET['id'] = 1
        request.GET['question'] = 1
        info = view_edit_question(request)
        self.assertEqual('/edit_test?id=1', info.location)
        questions = self.session.query(Question).all()
        self.assertEqual(2, len(questions))
        self.assertEqual(1, questions[0].question_num)
        self.assertEqual(2, questions[1].question_num)

        
        

        
        
        


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

"""class FunctionalTests(unittest.TestCase):
    
    def setUp(self):
        from pyquiz import main
        from webtest import TestApp
        app = main({})
        self.testapp = TestApp(app)

    def test_root(self):
        response = self.testapp.get('/', status=200)
        self.assertEquals(response.lxml.xpath('id("right")/h2/text()')[0], 'Pyramid links')"""

