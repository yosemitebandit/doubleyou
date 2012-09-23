import os
from flask import Flask, render_template, jsonify, abort, request
import csv
import datetime
import sys
import time
import math
import random
from mongoengine import connect

from models import Player, BodyMediaData, Question, Answer

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
    players = Player.objects(name=name)
    if not players:
        abort(404)
    player = players[0]

    answer_count = Answer.objects(player=player).count()
    return render_template('player_home.html', name=name
        , answer_count=answer_count)



def compute(player, requested_date, data):
    ''' compute all parameters..
    '''

    # calculatron
    ''' net caloric intake
    '''
    net = data.caloric_intake - data.caloric_output
    if net >= 100:
        net_calories = 3
    elif net >= -100 and net < 100:
        net_calories = 2
    else:
        net_calories = 1


    ''' activity calculator
    '''
    caloric_target = 2475  # parameterize later
    age = 39

    if player.gender == 'male':
        BMR = 66 + (6.23 * player.weight) + (12.7 * player.height) - (6.8 * age)
    else:
        BMR = 655 + (4.35 * player.weight) + (4.7 * player.height) - (4.7 * age)

    baseline = BMR * 1.2

    if data.caloric_output >= caloric_target + 200:
        physical_activity = 3
    elif data.caloric_output >= baseline + 350 and data.caloric_output < caloric_target + 200:
        physical_activity = 2
    else:
        physical_activity = 1


    ''' sleep calculator
    '''
    sleep_goal = 60*8   # parameterize one day, lalala

    # try to get the previous day
    previous_day = requested_date - datetime.timedelta(days=1)
    previous_day_data = BodyMediaData.objects(player=player
        , timestamp=previous_day)
    if not previous_day_data:
        # 100% weighted to current day
        percent_of_goal = data.lying_down / sleep_goal
        sleep_efficiency = data.sleep_duration / data.lying_down

        if percent_of_goal > 1:
            percent_score = 3
        elif percent_of_goal > 0.9:
            percent_score = 2
        else:
            percent_score = 1

        if sleep_efficiency >= 0.8:
            efficiency_score = 3
        elif sleep_efficiency > 0.6:
            efficiency_score = 2
        else:
            efficiency_score = 1

        if efficiency_score == 3 and percent_score == 3:
            time_slept = 3
        elif efficiency_score == 2 or percent_score == 2:
            time_slept = 2
        elif efficiency_score == 1 or percent_score == 1:
            time_slept = 1


    else:
        previous_day_data = previous_day_data[0]
        # 25% yesterday, 75% today
        percent_of_goal = data.lying_down / sleep_goal
        percent_of_goal_yesterday = previous_day_data.lying_down / sleep_goal
        sleep_efficiency = data.sleep_duration / data.lying_down
        sleep_efficiency_yesterday = previous_day_data.sleep_duration / data.lying_down

        if percent_of_goal*0.75 + percent_of_goal_yesterday*0.25 > 1:
            percent_score = 3
        if percent_of_goal*0.75 + percent_of_goal_yesterday*0.25 > 0.9:
            percent_score = 2
        else:
            percent_score = 1

        if sleep_efficiency*0.75 + sleep_efficiency_yesterday*0.25 >= 0.8:
            efficiency_score = 3
        if sleep_efficiency*0.75 + sleep_efficiency_yesterday*0.25 >= 0.6:
            efficiency_score = 2
        else:
            efficiency_score = 1

        if efficiency_score == 3 and percent_score == 3:
            time_slept = 3
        elif efficiency_score == 2 or percent_score == 2:
            time_slept = 2
        elif efficiency_score == 1 or percent_score == 1:
            time_slept = 1
    

    ''' question score
    '''
    yesterday = requested_date - datetime.timedelta(days=1)
    question_responses = Answer.objects(player=player
            , timestamp__gte=yesterday, timestamp__lte=requested_date).count()

    if question_responses > 10:
        question_responses = 10

    return {
        'time_slept': time_slept
        , 'net_calories': net_calories
        , 'physical_activity': physical_activity
        , 'question_responses': question_responses
        , 'requested_date': requested_date.strftime('%d/%m/%Y')
    }


''' API routes
'''
@app.route('/api/players/<name>/<date>')
def player_data(name, date):
    ''' date is of the format 20120910 or YYmd
    '''
    players = Player.objects(name=name)
    if not players:
        abort(404)
    player = players[0]

    requested_date = datetime.datetime.fromtimestamp(time.mktime(
        time.strptime(date, '%Y%m%d')))

    data = None
    # what if 2010??
    while not data:
        data = BodyMediaData.objects(player=player, timestamp=requested_date)
        requested_date = requested_date - datetime.timedelta(days=1)
    data = data[0]

    todays_result = compute(player, requested_date, data)

    # total-score computation
    total_score = 0
    for i in [0,1,2]:
        requested_date = requested_date - datetime.timedelta(days=i)
        r = compute(player, requested_date, data)

        if i == 0:
            total_score += 0.6*(10*r['physical_activity'] + r['question_responses'] + 10*r['net_calories'] + 10*r['time_slept'])
        elif i == 1:
            total_score += 0.3*(10*r['physical_activity'] + r['question_responses'] + 10*r['net_calories'] + 10*r['time_slept'])
        elif i == 2:
            total_score += 0.1*(10*r['physical_activity'] + r['question_responses'] + 10*r['net_calories'] + 10*r['time_slept'])


    todays_result['total_score'] = int(total_score)

    return jsonify(todays_result)


@app.route('/api/players/<name>/answers', methods=['POST'])
def player_answers(name):
    players = Player.objects(name=name)
    if not players:
        abort(404)
    player = players[0]

    question_id = request.form.get('question_id', '')
    response = request.form.get('response', '') 
    question = Question.objects(id=question_id)[0]

    new_answer = Answer(
        question = question
        , player = player
        , data = int(response)
        , timestamp = datetime.datetime.utcnow()
    )
    new_answer.save()

    player.update(set__last_answer_time=datetime.datetime.utcnow())
    answer_count = Answer.objects(player=player).count()

    return jsonify({'status': 'ok', 'answer_count': answer_count})


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
        , 'response_0': q.possible_responses[0]
        , 'response_1': q.possible_responses[1]
        , 'response_2': q.possible_responses[2]
        , 'response_3': q.possible_responses[3]
        , 'classification': q.classification
        , 'question_id': str(q.id)
    })


''' seeding the database
'''
@app.route('/api/seed/destroy')
def destroy_seed():
    objects = []
    objects.extend(Question.objects())
    objects.extend(Player.objects())
    objects.extend(Answer.objects())
    objects.extend(BodyMediaData.objects())

    for o in objects:
        o.delete()

    return 'ouch'


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

    q = Question(
        prompt = 'How would you rate your asthma control today?'
        , possible_responses = ['1', '2', '3', '4']
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
        name = 'matt'
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
    player = Player.objects(name='matt')[0]

    # in 'static' dir we have an excel file with Body Media data rows
    data_path = 'static/data/v2.csv'
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
                    time.strptime(row[0], '%Y%m%d.000000')))
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
