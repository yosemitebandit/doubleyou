import os
from flask import Flask, render_template, jsonify, abort
import csv
import datetime
import sys
import time
import math
import random
from mongoengine import connect

from models import Player, BodyMediaData, Question

app = Flask(__name__)


# get env-var
# the MONGOLAB_URI env-var is mongodb://username:password@host:port/database
if not os.environ['MONGOLAB_URI']:
    print 'please set the env var'
    sys.exit(0)

m = os.environ['MONGOLAB_URI']
database = m.split('/')[3]
username = database
port = int(m.split('/')[2].split(':')[2])
[password, host] = m.split('/')[2].split(':')[1].split('@')

connect(database, host=host, port=port, username=username, password=password)


''' meta routes
'''
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/about')
def about():
    return render_template('about.html')


''' player data routes
'''
@app.route('/players/<name>')
def player_home(name):
    return render_template('player_home.html', name=name)


''' API routes
'''
@app.route('/api/players/<name>')
def player_data(name):

    players = Player.objects(name=name)
    if not players:
        abort(404)
    player = players[0]

    player_data = BodyMediaData.objects(player=player)

    # calculate..

    response = {
        'time_slept': 3
        , 'net_calories': 2
        , 'physical_activity': 1
        , 'question_responses': 3
    }

    return jsonify(response)


@app.route('/api/players/<name>/questions')
def player_questions(name):
    ''' get a relevant question
    '''

    '''
    players = Player.objects(name=name)
    if not players:
        abort(404)
    player = players[0]
    '''

    questions = Question.objects()
    index = int(math.floor(random.random()*5))

    q = questions[index]

    return jsonify({
        'prompt': q.prompt
        , 'possible_responses': q.possible_responses
        , 'classification': q.classification
    })


''' seeding the database
'''
@app.route('/api/seed/questions')
def seed_questions():
    questions = Question.objects()
    if questions:
        return 'already seeded'

    q = Question(
        prompt = 'How many times did you wake up last night?'
        , possible_responses = ['0', '1', '2', '3']
        , classification = 'morning'
    )
    q.save()

    q = Question(
        prompt = 'How bad were your asthma symptoms when you woke up this morning?'
        , possible_responses = ['not bad at all', 'a little bad', 'somewhat bad', 'very bad']
        , classification = 'morning'
    )
    q.save()

    q = Question(
        prompt = 'How rested do you feel this morning?'
        , possible_responses = ['well rested', 'somewhat', 'a little', 'not at all']
        , classification = 'morning'
    )
    q.save()

    q = Question(
        prompt = 'How much trouble did you have falling asleep?'
        , possible_responses = ['no trouble', 'a little trouble', 'some trouble', 'a lot of trouble']
        , classification = 'morning'
    )
    q.save()

    q = Question(
        prompt = 'How limited were you in activities because of your asthma?'
        , possible_responses = ['not at all', 'a little', 'somewhat', 'a lot']
        , classification = 'night'
    )
    q.save()

    q = Question(
        prompt = 'How much shortness did you experience because of your asthma?'
        , possible_responses = ['none at all', 'a little', 'some', 'a lot']
        , classification = 'night'
    )
    q.save()

    q = Question(
        prompt = 'How much time did you wheeze today?'
        , possible_responses = ['none at all', 'a little of the time', 'some of the time', 'a lot of the time']
        , classification = 'night'
    )
    q.save()

    q = Question(
        prompt = 'How many times did you use your inhaler today?'
        , possible_responses = ['zero', '1-2', '3-4', '5+']
        , classification = 'night'
    )
    q.save()

    q = Question(
        prompt = 'How much did your asthma affect your exercise today?'
        , possible_responses = ['not at all', 'a little', 'somewhat', 'a lot']
        , classification = 'night'
    )
    q.save()

    return 'ok'


@app.route('/api/seed/players')
def seed_players():
    players = Player.objects()
    if players:
        return 'already seeded'

    new_player = Player(
        name = 'Matt B'
        , signup_time = datetime.datetime.utcnow()
        , birthday = datetime.date(1988, 2, 3)
        , height = '77'
        , weight = '165'
        , smoker = False
        , gender = 'male'
    )
    new_player.save()

    return 'ok'


@app.route('/api/seed/bmdata')
def seed_bmdata():
    ''' hacked way to get our static data into the db
    '''
    # if there is no body media data in the db
    bm_data = BodyMediaData.objects()
    if bm_data:
        return 'already seeded'

    # attach to a specific player
    player = Player.objects(name='Matt B')[0]

    # in 'static' dir we have an excel file with Body Media data rows
    data_path = 'static/data/v1.csv'
    with open(data_path, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        ''' iterate over the rows and inject body media entries
        assuming this column order in the excel file:
        timestamp, lying down, sleep duration, calories in, calories out,
        average MET, sed, mod, vigorous
        '''
        count = 0
        for row in reader:
            if count == 0:
                count += 1
                continue

            bmdata = BodyMediaData(
                timestamp = datetime.datetime.fromtimestamp(time.mktime(
                    time.strptime(row[0], '%m/%d/%y')))
                , lying_down = float(row[1])
                , sleep_duration = float(row[2])
                , caloric_intake = float(row[3])
                , caloric_output = float(row[4])
                , average_met = float(row[5])
                , sedentary_activity_duration = float(row[6])
                , moderate_activity_duration = float(row[7])
                , vigorous_activity_duration = float(row[8])
                , player=player
            )
            bmdata.save()

    return 'ok'


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
