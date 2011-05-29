"""
This file is used to create the schema used for the test
creation form.
"""

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
    """
    Schema that stores a single answer to a question.
    """
    text = SchemaNode(String())
    correct = SchemaNode(Boolean())

class Answers(SequenceSchema):
    """
    Schema used to store the sequence AnswerSchema classes
    for each quesiton in the test.
    """
    answers = AnswerSchema()

class QuestionSchema(MappingSchema):
    """
    Schema that stores a single question to a test.
    """
    text = SchemaNode(String())
    answers = Answers()

class Questions(SequenceSchema):
    """
    Schema used to store the sequence of QuestionSchema
    classes representing each quesiton in the test.
    """
    questions = QuestionSchema()

class TestSchema(Schema):
    """
    Schema that stores the test being created.
    """
    name = SchemaNode(String())
    class_id = SchemaNode(String())
    questions = Questions()


