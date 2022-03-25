from flask import Flask, render_template, abort, request, redirect
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from werkzeug import exceptions
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField
from wtforms.validators import DataRequired, Length, URL
from datetime import datetime
import os

# from costs import user_costs
# import random

currentTime = datetime.now()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
csrf = CSRFProtect(app)


class UserCost(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    cover = db.Column(db.Text)
    items = db.relationship('CostItem', backref='list', lazy=True)

    def __repr__(self):
        return f'<UserCost {self.name}>'


class CostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    cost_id = db.Column(db.Integer, db.ForeignKey('user_cost.id'), nullable=False)


class CreateUserCost(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(min=3, max=80)])
    cover = StringField('Ссылка на обложку', validators=[DataRequired(), URL()])


@app.route('/')
def homepage():
    user_costs = UserCost.query.all()
    return render_template('index.html',
                           title='Gde moi den`gi?',
                           user_costs=user_costs)


@app.route('/about')
def about():
    return render_template('home.html',
                           title='Gde moi den`gi?')


@app.route('/user-costs/<int:cost_id>')
def get_cost(cost_id):
    user_cost = UserCost.query.get_or_404(escape(cost_id))
    return render_template('list.html', user_cost=user_cost)


@app.route('/user-costs/create', methods=['GET', 'POST'])
def create_cost():
    create_user_cost_form = CreateUserCost()
    if create_user_cost_form.validate_on_submit():
        name = request.form.get('name')
        cover = request.form.get('cover')
        new_cost = UserCost(name=name, cover=cover)
        db.session.add(new_cost)
        db.session.commit()
        return redirect('/')
    return render_template('create_cost.html', form=create_user_cost_form)


@app.route('/search')
def search():
    text = escape(request.args.get('text', ''))
    selected_costs = UserCost.query.filter(UserCost.name.like(f'%{text}%')).all()
    return render_template('index.html', user_costs=selected_costs)


@app.errorhandler(exceptions.NotFound)
def not_found(error):
    return render_template('404.html'), exceptions.NotFound.code


if __name__ == '__main__':
    app.run()
