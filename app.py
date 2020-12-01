from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, RadioField
from wtforms.validators import InputRequired
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random
import json
from http.client import HTTPException


app = Flask(__name__)      # объявим экземпляр фласка
app.secret_key = "randomstringstepiktranslate"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://yllkocmnskcxyq:d98afb9efd3151fa1fc2cc5687480a2e22cfd54ec995be0644b977d412098a41@ec2-54-247-103-43.eu-west-1.compute.amazonaws.com:5432/d97uuhg52vb66b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


teachers_goals_association = db.Table(
    "teachers_goals",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teachers.id")),
    db.Column("goal_id", db.Integer, db.ForeignKey("goals.id")),
)


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    about = db.Column(db.String)
    rating = db.Column(db.Float)
    picture = db.Column(db.String)
    price = db.Column(db.Float)
    email = db.Column(db.String)
    free = db.Column(db.String)
    bookings = db.relationship("Booking")
    goals = db.relationship(
        "Goal", secondary=teachers_goals_association, back_populates="teachers"
    )


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String)
    hour = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    teacher = db.relationship("Teacher")
    name = db.Column(db.String)
    phone = db.Column(db.String)


class Request(db.Model):
    __tablename__ = "request"
    id = db.Column(db.Integer, primary_key=True)
    hour = db.Column(db.String)
    name = db.Column(db.String)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"))
    goal = db.relationship("Goal")
    phone = db.Column(db.String)


class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    alias = db.Column(db.String)
    teachers = db.relationship(
        "Teacher", secondary=teachers_goals_association, back_populates="goals"
    )


title = "Stepik Translate"
subtitle = "Все репетиторы"
description = "Лучшие репетиторы"

days = {
    'mon': 'Понедельник',
    'tue': 'Вторник',
    'wed': 'Среда',
    'thu': 'Четверг',
    'fri': 'Пятница',
    'sat': 'Суббота',
    'sun': 'Воскресенье'
}

with open("data/goals.json", "r") as f:
    goals = json.load(f)

with open("data/teachers.json", "r") as f:
    teachers_json = json.load(f)

goals.update({'dev': 'Для программирования'})


def get_teachers(teachers_list):
    teachers = {}
    for item in teachers_list:
        if item['id'] in [8, 9, 10, 11]:
            item['goals'].append('dev')
        teachers.update({item['id']: item})
    return teachers


def add_request(client_goal, client_time, client_name, client_phone):
    req = Request(
        name=client_name,
        hour=client_time,
        goal=db.session.query(Goal).filter(Goal.alias == client_goal).first(),
        phone=client_phone
    )
    db.session.add(req)
    db.session.commit()


def add_booking(client_weekday, client_time, client_teacher, client_name, client_phone):
    time, _ = client_time.split(':')
    booking = Booking(
        day=client_weekday,
        name=client_name,
        hour=time,
        phone=client_phone,
        teacher=db.session.query(Teacher).get(client_teacher)
    )
    db.session.add(booking)
    db.session.commit()


# заполняем БД
if db.session.query(Goal).count() == 0:
    with open("data/goals.json", "r") as f:
       goals = json.load(f)

    for goal in goals:
        db.session.add(Goal(name=goals[goal], alias=goal))

    db.session.commit()
    goals_db = db.session.query(Goal).all()

    goals_list = {}
    for goal in goals_db:
        goals_list[goal.alias] = goal

    for teacher in teachers_json:

        t = Teacher(
                name=teacher['name'],
                about=teacher['about'],
                rating=teacher['rating'],
                picture=teacher['picture'],
                price=teacher['price'],
                free=json.dumps(teacher['free'])
            )

        for goal in teacher['goals']:
            t.goals.append(goals_list[goal])

        db.session.add(t)

    db.session.commit()

# заполняем БД - окончание


# создание форм
class RequestForm(FlaskForm):
    clientGoal = RadioField('Какая цель занятий?', choices=[
        ('travel', 'Для путешествий'),
        ('study', 'Для школы'),
        ('work', 'Для работы'),
        ('move', 'Для переезда'),
        ('dev', 'Для программирования')
    ])
    clientTime = RadioField('Сколько времени есть?', choices=[
        ('1-2', '1-2 часа в неделю'),
        ('3-5', '3-5 часов в неделю'),
        ('5-7', '5-7 часов в неделю'),
        ('7-10', '7-10 часов в неделю')
    ])
    clientName = StringField("Вас зовут", [InputRequired(message="Необходимо указать имя")])
    clientPhone = StringField("Ваш телефон", [InputRequired(message="Необходимо указать телефон")])


class BookingForm(FlaskForm):
    clientWeekday = HiddenField()
    clientTime = HiddenField()
    clientTeacher = HiddenField()
    clientName = StringField("Вас зовут", [InputRequired(message="Необходимо указать имя")])
    clientPhone = StringField("Ваш телефон", [InputRequired(message="Необходимо указать телефон")])


@app.route('/')
def route_index():
    teachers = db.session.query(Teacher).all()
    teacher_c = db.session.query(Teacher).count()
    return render_template('index.html', title=title, subtitle=subtitle, description=description, teachers=random.sample(teachers, 6), teachers_c=teacher_c, goals=goals)


@app.route('/teachers/')
def route_teachers():
    sort = request.values.get('sort', 'rating')
    if sort == 'rating':
        teachers = db.session.query(Teacher).order_by(Teacher.rating.desc()).all()
    else:
        teachers = db.session.query(Teacher).order_by(Teacher.price.desc()).all()
    teacher_c = db.session.query(Teacher).count()
    return render_template('index.html', title=title, subtitle=subtitle, description=description, teachers=teachers, teachers_c=teacher_c, goals=goals)


@app.route('/goal/<goal>/')
def route_goal(goal):
    teachers = db.session.query(Teacher).order_by(Teacher.rating.desc()).all()

    teacher_list = []
    for item in teachers:
        if 0 != len(list(filter(lambda x: x.alias == goal, item.goals))):
            teacher_list.append(item)

    return render_template(
        'goal.html',
        title=title,
        subtitle=subtitle,
        description=description,
        teachers=teacher_list,
        goals=goals,
        goal=goal
    )


@app.route('/profile/<int:teacher_id>/')
def route_profile(teacher_id):

    # teacher = db.session.query(Teacher).get_or_404(teacher_id)
    teacher = db.session.query(Teacher).get(teacher_id)

    if not teacher:
        raise HTTPException(code=404)

    schedule = json.loads(teacher.free)

    for item in teacher.bookings:
        schedule[item.day][str(item.hour) + ':00'] = False

    return render_template(
        'profile.html',
        title=title,
        subtitle=subtitle,
        description=description,
        teacher=teacher,
        schedule=schedule,
        days=days,
        goals=goals
    )


@app.route('/request/', methods=["GET", "POST"])
def route_request():
    # создаем форму
    form = RequestForm()

    if request.method == "POST":
        # получаем данные
        client_goal = form.clientGoal.data
        client_time = form.clientTime.data
        client_name = form.clientName.data
        client_phone = form.clientPhone.data

        add_request(client_goal, client_time, client_name, client_phone)

        return render_template(
            'request_done.html',
            title=title,
            subtitle=subtitle,
            description=description,
            goals=goals,
            clientGoal=client_goal,
            clientTime=client_time,
            clientName=client_name,
            clientPhone=client_phone
        )

    return render_template(
        'request.html',
        title=title,
        subtitle=subtitle,
        description=description,
        form=form
    )


@app.route('/booking/<int:teacher_id>/<day>/<int:hour>', methods=["GET", "POST"])
def route_booking(teacher_id, day, hour):
    teachers = get_teachers(teachers_json)

    # создаем форму
    form = BookingForm()

    if request.method == "POST":
        # получаем данные
        client_weekday = form.clientWeekday.data
        client_time = form.clientTime.data
        client_teacher = form.clientTeacher.data
        client_name = form.clientName.data
        client_phone = form.clientPhone.data

        add_booking(client_weekday, client_time, client_teacher, client_name, client_phone)

        return render_template(
            'booking_done.html',
            title=title,
            subtitle=subtitle,
            description=description,
            teacher=teachers[teacher_id],
            clientWeekday=client_weekday,
            clientTime=client_time,
            clientTeacher=client_teacher,
            clientName=client_name,
            clientPhone=client_phone,
            days=days,
            day=day,
            hour=hour
        )

    return render_template(
        'booking.html',
        title=title,
        subtitle=subtitle,
        description=description,
        teacher=teachers[teacher_id],
        days=days,
        day=day,
        hour=hour,
        form=form
    )


if __name__ == '__main__':
    # app.run('0.0.0.0',8000)    # запустим сервер на 8000 порту!
    app.run()    # запустим сервер на 8000 порту!
