import json
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)


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
@app.route('/players/<name>/questions')
def player_questions(name):
    return render_template('player_questions.html', name=name)

@app.route('/players/<name>/dashboard')
def player_dashboard(name):
    return render_template('player_dashboard.html', name=name)

@app.route('/players/<name>')
def player_home(name):
    return render_template('player_home.html', name=name)


''' API routes
'''
@app.route('/api/players/<name>')
def player_data(name):
    f = open('static/json/data.json', 'r')
    data = json.loads(f.read())
    return jsonify(data)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
