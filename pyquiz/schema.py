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


