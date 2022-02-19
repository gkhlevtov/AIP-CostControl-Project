from flask import Flask, render_template, abort, request
from markupsafe import escape
from werkzeug import exceptions
from os import environ
from datetime import datetime
from months import months_num, months_costs

currentTime = datetime.now()

app = Flask(__name__)
app.secret_key = environ['APP_SECRET_KEY']


@app.route('/')
def homepage():
    return render_template('home.html',
                           title='Gde moi den`gi?')


@app.route('/user-costs/')
def userpage():
    return render_template('index.html',
                           title='Gde moi den`gi?',
                           months_costs=months_costs)


@app.route('/user-costs/<month_name>')
def get_costs(month_name):
    if month_name not in months_num:
        abort(exceptions.NotFound.code)
    return render_template('list.html', months_cost=months_costs[months_num[month_name] - 1])


@app.route('/search')
def search():
    text = escape(request.args.get('text', '').lower())
    selected_costs = []
    for months_cost in months_costs:
        for item in months_cost['items']:
            if text in item['title'].lower():
                selected_costs.append(months_cost)
            continue
    print(selected_costs)
    return render_template('index.html', months_costs=selected_costs)


@app.errorhandler(exceptions.NotFound)
def not_found(error):
    return render_template('404.html'), exceptions.NotFound.code


if __name__ == '__main__':
    app.run()
