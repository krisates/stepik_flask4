from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, RadioField
from wtforms.validators import InputRequired
from flask_wtf.csrf import CSRFProtect
import random
import json


app = Flask(__name__)      # объявим экземпляр фласка
app.secret_key = "randomstringstepiktranslate"
csrf = CSRFProtect(app)

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
    with open('data/request.json', "r") as r:
        records = json.load(r)
    records.append({'goal': client_goal, 'hour': client_time, 'name': client_name, 'phone': client_phone})
    with open('data/request.json', "w") as w:
        json.dump(records, w)


def add_booking(client_weekday, client_time, client_teacher, client_name, client_phone):
    with open('data/booking.json', "r") as r:
        records = json.load(r)
    records.append({'day': client_weekday, 'hour': client_time, 'teacher': client_teacher, 'name': client_name, 'phone': client_phone})
    with open('data/booking.json', "w") as w:
        json.dump(records, w)


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
        ('1-2', '1-2 часа в&nbsp;неделю'),
        ('3-5', '3-5 часов в&nbsp;неделю'),
        ('5-7', '5-7 часов в&nbsp;неделю'),
        ('7-10', '7-10 часов в&nbsp;неделю')
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
    return render_template('index.html', title=title, subtitle=subtitle, description=description, teachers=random.sample(teachers_json, 6), goals=goals)


@app.route('/teachers/')
def route_teachers():
    return render_template('index.html', title=title, subtitle=subtitle, description=description, teachers=teachers_json, goals=goals)


@app.route('/goal/<goal>/')
def route_goal(goal):
    teachers = []
    for item in teachers_json:
        if item['id'] in [8, 9, 10, 11]:
            item['goals'].append('dev')
        if goal in item['goals']:
            teachers.append(item)
    return render_template(
        'goal.html',
        title=title,
        subtitle=subtitle,
        description=description,
        teachers=sorted(teachers, key=lambda x: x['rating'], reverse=True),
        goals=goals,
        goal=goal
    )


@app.route('/profile/<int:teacher_id>/')
def route_profile(teacher_id):
    teachers = get_teachers(teachers_json)

    schedule = {}
    for item, val in teachers[teacher_id]['free'].items():
        lessons = []
        for hour, is_free in val.items():
            if is_free is True:
                lessons.append(hour)
        schedule.update({item: lessons})
    return render_template('profile.html', title=title, subtitle=subtitle, description=description, teacher=teachers[teacher_id], schedule=schedule, days=days, goals=goals)


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
    #app.run('0.0.0.0',8000)    # запустим сервер на 8000 порту!
    app.run()    # запустим сервер на 8000 порту!
