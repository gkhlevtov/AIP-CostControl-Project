from flask import Flask, render_template, abort, request
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from werkzeug import exceptions
from os import environ
from datetime import datetime
from costs import user_costs

currentTime = datetime.now()

app = Flask(__name__)
# app.secret_key = environ['APP_SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class UserCost(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    cover = db.Column(db.Text)
    items = db.relationship('TodoItem', backref='list', lazy=True)

    def __repr__(self):
        return f'<TodoList {self.name}>'


class CostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todo_list.id'), nullable=False)


@app.route('/')
def homepage():
    return render_template('home.html',
                           title='Gde moi den`gi?')


@app.route('/user-costs/')
def userpage():
    return render_template('index.html',
                           title='Gde moi den`gi?',
                           user_costs=user_costs)


@app.route('/user-costs/<int:cost_id>')
def get_costs(cost_id):
    """user_cost = UserCost.query.get(cost_id)
    print(user_cost)"""
    if cost_id > len(user_costs) or cost_id <= 0:
        abort(exceptions.NotFound.code)
    return render_template('list.html', user_cost=user_costs[cost_id - 1])


@app.route('/search')
def search():
    text = escape(request.args.get('text', '').lower())
    selected_costs = []
    for user_cost in user_costs:
        for item in user_cost['items']:
            if text in item['title'].lower():
                selected_costs.append(user_cost)
            continue
    print(selected_costs)
    return render_template('index.html', user_costs=selected_costs)


@app.errorhandler(exceptions.NotFound)
def not_found(error):
    return render_template('404.html'), exceptions.NotFound.code


if __name__ == '__main__':
    app.run()
