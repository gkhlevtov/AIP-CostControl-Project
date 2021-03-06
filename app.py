from flask import Flask, render_template, request, redirect
from markupsafe import escape
from werkzeug import exceptions
from forms import csrf, LoginForm, CreateUserCost, CreateItem, RegistrationForm
from models import db, bcrypt, User, UserCost, CostItem
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from random import sample
from colors import rgb
from os import environ

app = Flask(__name__)
uri = environ.get('DATABASE_URL')
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
login_manager = LoginManager(app)
csrf.init_app(app)
db.app = app
db.init_app(app)
db.create_all()
bcrypt.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.route('/')
def homepage():
    if current_user.is_authenticated:
        user_costs = UserCost.query.filter_by(user_id=current_user.id)
    else:
        user_costs = []
    return render_template('index.html',
                           title='Gde moi den`gi?',
                           user_costs=user_costs)


@app.route('/about')
def about():
    return render_template('home.html',
                           title='Gde moi den`gi?')


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        user = User()
        user.email = email
        user.nickname = nickname
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/')
    return render_template('register.html', form=register_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/')
        else:
            return render_template('login.html', form=login_form)
    return render_template('login.html', form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/user-costs/<int:cost_id>', methods=['GET', 'POST'])
def get_cost(cost_id):
    user_cost = UserCost.query.get_or_404(escape(cost_id))
    if not current_user.is_authenticated:
        raise exceptions.Forbidden()
    elif current_user.id != user_cost.user_id:
        raise exceptions.Forbidden()

    values = []
    titles = []
    main_colors = []
    border_colors = []
    clr = [[f'rgba({x[0]}, {x[1]}, {x[2]}, 0.8)', f'rgba({x[0]}, {x[1]}, {x[2]}, 1)']
           for x in sample(rgb, k=len(user_cost.items))]
    for el in clr:
        main_colors.append(el[0])
        border_colors.append(el[1])

    for item in user_cost.items:
        values.append(int(item.value))
        titles.append(item.title)

    create_item_form = CreateItem()
    if create_item_form.validate_on_submit():
        title = request.form.get('title')
        value = int(request.form.get('value'))
        new_item = CostItem(title=title,
                            value=value,
                            cost_id=cost_id)
        db.session.add(new_item)
        db.session.commit()
        return redirect(f'/user-costs/{cost_id}')

    return render_template('list.html',
                           user_cost=user_cost,
                           form=create_item_form,
                           len=len,
                           cost_id=cost_id,
                           values=values,
                           titles=titles,
                           main_colors=main_colors,
                           border_colors=border_colors)


@app.route('/user-costs/create', methods=['GET', 'POST'])
@login_required
def create_cost():
    create_user_cost_form = CreateUserCost()
    if create_user_cost_form.validate_on_submit():
        name = request.form.get('name')
        cover = request.form.get('cover')
        user_id = current_user.id
        new_cost = UserCost(name=name, cover=cover, user_id=user_id)
        db.session.add(new_cost)
        db.session.commit()
        return redirect('/')
    return render_template('create_cost.html', form=create_user_cost_form)


@app.route('/search')
def search():
    text = escape(request.args.get('text', ''))
    selected_costs = UserCost.query.filter(UserCost.name.ilike(f'%{text}%')).all()
    return render_template('index.html', user_costs=selected_costs)


@app.errorhandler(exceptions.NotFound)
def not_found(error):
    return render_template('404.html'), exceptions.NotFound.code


@app.errorhandler(exceptions.Forbidden)
def forbidden(error):
    return render_template('403.html'), exceptions.Forbidden.code


if __name__ == '__main__':
    app.run()
