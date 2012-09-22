from mongoengine import (Document, StringField, DateTimeField, ReferenceField
        , IntField, BooleanField, FloatField, ListField)

class Player(Document):
    name = StringField()
    signup_time = DateTimeField()
    #friends = ListField(ReferenceField('Player'))
    last_answer_time = DateTimeField()
    twitter = StringField()
    birthday = DateTimeField()
    height = IntField()
    weight = IntField()
    smoker = BooleanField()
    gender = StringField()


class Question(Document):
    prompt = StringField()
    possible_responses = ListField(StringField())
    classification = StringField()


class Answer(Document):
    question = ReferenceField(Question)
    player = ReferenceField(Player)
    data = IntField()
    timestamp = DateTimeField()


class BodyMediaData(Document):
    ''' we assume one entry for each day
    all times in seconds
    '''
    timestamp = DateTimeField()
    lying_down = FloatField()
    sleep_duration = FloatField()
    caloric_intake = FloatField()
    caloric_output = FloatField()
    average_met = FloatField()
    sedentary_activity_duration = FloatField()
    moderate_activity_duration = FloatField()
    vigorous_activity_duration = FloatField()
    player = ReferenceField(Player)

