import datetime
import os

from flask import Flask, render_template, redirect, request, jsonify
from data import db_session, route_info
from data.main_table import MainTable
from data.route_info import blueprint
from data.routes import Routes
from data.sts import Sts
from forms.add_edit_form import AddEditForm
from forms.add_edit_route_form import AddEditRouteForm
from forms.add_edit_st_form import AddEditStForm


# функция проверки наложения интервалов событий
def check_interval(begin, end, checking_data):
    for i in checking_data:
        if begin < i.end_time <= end:
            return i
        elif begin <= i.begin_time < end:
            return i
        elif i.begin_time <= begin <= end <= i.end_time:
            return i
    return None


# функция преобразования строки в datetime
def string_to_datetime(string):
    string = [int(i) for i in string.split(':')]
    return datetime.datetime(*string)


# функция проверки корректности ip-адреса
def correct_ip(ip_string):
    ip_list = ip_string.split('.')
    if len(ip_list) != 4:
        return False
    if not all(list(map(lambda x: x.isdigit(), ip_list))):
        return False
    if not all(list(map(lambda x: 0 < int(x) < 255, ip_list))):
        return False
    return True


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


# функция возвращает список всех событий
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def events():
    db_sess = db_session.create_session()
    data = db_sess.query(MainTable).all()

    # проверяем наличия ключа в параметрах http-запроса (нужно для удаления событий)
    if 'st_number' in request.args.keys():
        id_row = request.args['st_number']
        db_sess.query(MainTable).filter(MainTable.id == id_row).delete()
        db_sess.commit()
        data = db_sess.query(MainTable).all()

    return render_template("events.html", data=enumerate(data))


# функция реализует форму редактирования выбранного события
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    db_sess = db_session.create_session()
    form = AddEditForm()
    # список всех маршрутов
    routes_list = [(i.route, i.route) for i in db_sess.query(Routes).all()]
    # список всех табло
    sts_list = [(i.id, i.id) for i in db_sess.query(Sts).all()]
    id_row = 1
    # проверяем наличие параметра, содержащего id редактируемого события
    if 'st_number' in request.args.keys():
        id_row = request.args['st_number']
    form.route_number.choices = routes_list
    form.st_number.choices = sts_list
    data = db_sess.query(MainTable).filter(MainTable.id == int(id_row)).first()
    form.begin_time.data = data.begin_time
    form.end_time.data = data.end_time
    form.up_time.data = data.up_time
    form.st_number.data = str(data.n_st_id)
    form.route_number.data = data.n_route.route
    # обрабатываем нажатие на кнопку
    if form.validate_on_submit():
        now = datetime.datetime.now()
        begin_time = datetime.datetime(year=now.year, month=now.month, day=now.day,
                                       hour=int(form.begin_time.raw_data[0][:2]),
                                       minute=int(form.begin_time.raw_data[0][3:]))
        end_time = datetime.datetime(year=now.year, month=now.month, day=now.day,
                                     hour=int(form.end_time.raw_data[0][:2]),
                                     minute=int(form.end_time.raw_data[0][3:]))
        up_time = datetime.datetime(year=now.year, month=now.month, day=now.day,
                                    hour=int(form.up_time.raw_data[0][:2]),
                                    minute=int(form.up_time.raw_data[0][3:]))
        # проверки на очередность времени
        if not (begin_time <= end_time):
            return render_template('add_edit_event.html', title='Изменить', form=form,
                                   message="Время окончания     события предшествует времени его начала")
        if not (end_time < up_time):
            return render_template('add_edit_event.html', title='Изменить', form=form,
                                   message="Время вылета предшествует времени окончания события")
        # проверяем, чтобы наше событие не накладывалось на существующие, начало одного и окончание другого
        # могут совпадать
        checking_data = db_sess.query(MainTable).filter(MainTable.n_st_id == int(form.st_number.raw_data[0]),
                                                        MainTable.id != id_row).all()
        check_result = check_interval(begin_time, end_time, checking_data)
        if check_result is not None:
            return render_template('add_edit_event.html', title='Изменить', form=form,
                                   message="Для этого табло уже есть пересекающееся событие с интервалом " +
                                           f"c {check_result.begin_time.strftime('%H:%M')} по " +
                                           f"{check_result.end_time.strftime('%H:%M')} конец одного события пожет" +
                                           "совпадать с началом другого")

        route_data = db_sess.query(Routes).filter(Routes.route == form.route_number.raw_data[0]).first()

        edited_row = MainTable()
        edited_row.id = id_row
        edited_row.n_route_id = route_data.id
        edited_row.begin_time = begin_time
        edited_row.end_time = end_time
        edited_row.up_time = up_time
        edited_row.n_st_id = form.st_number.raw_data[0]

        # удаляем старую запись и делаем новую
        db_sess.query(MainTable).filter(MainTable.id == id_row).delete()
        db_sess.commit()
        db_sess.add(edited_row)
        db_sess.commit()
        return redirect('/')

    return render_template('add_edit_event.html', title='Изменить', form=form)


# функция реализует форму добавления нового события
@app.route("/add", methods=['GET', 'POST'])
def add():
    db_sess = db_session.create_session()
    # список всех маршрутов
    routes_list = [(i.route, i.route) for i in db_sess.query(Routes).all()]
    # список всех табло
    sts_list = [(i.id, i.id) for i in db_sess.query(Sts).all()]
    form = AddEditForm()
    form.route_number.choices = routes_list
    form.st_number.choices = sts_list
    form.begin_time.data = datetime.datetime.now()
    form.end_time.data = datetime.datetime.now() + datetime.timedelta(hours=2, minutes=20)
    form.up_time.data = datetime.datetime.now() + datetime.timedelta(hours=3)
    form.submit.label.text = 'Добавить'
    # обрабатываем нажатие на кнопку
    if form.validate_on_submit():
        now = datetime.datetime.now()
        begin_time = datetime.datetime(year=now.year, month=now.month, day=now.day,
                                       hour=int(form.begin_time.raw_data[0][:2]),
                                       minute=int(form.begin_time.raw_data[0][3:]))
        end_time = datetime.datetime(year=now.year, month=now.month, day=now.day,
                                     hour=int(form.end_time.raw_data[0][:2]),
                                     minute=int(form.end_time.raw_data[0][3:]))
        # проверки на очередность времени
        if not (form.begin_time.data <= form.end_time.data):
            return render_template('add_edit_event.html', title='Добавить', form=form,
                                   message="Время окончания события предшествует времени его начала")
        if not (form.end_time.data < form.up_time.data):
            return render_template('add_edit_event.html', title='Добавить', form=form,
                                   message="Время вылета предшествует времени окончания события")
        # проверяем, чтобы наше событие не накладывалось на существующие, начало одного и окончание другого
        # могут совпадать
        checking_data = db_sess.query(MainTable).filter(MainTable.n_st_id == int(form.st_number.raw_data[0])).all()
        check_result = check_interval(begin_time, end_time, checking_data)
        if check_result is not None:
            return render_template('add_edit_event.html', title='Добавить', form=form,
                                   message="Для этого табло уже есть пересекающееся событие с интервалом " +
                                           f"c {check_result.begin_time.strftime('%H:%M')} по " +
                                           f"{check_result.end_time.strftime('%H:%M')} конец одного события пожет" +
                                           "совпадать с началом другого")
        route_data = db_sess.query(Routes).filter(Routes.route == form.route_number.raw_data[0]).first()
        now = datetime.datetime.now()
        begin_time = datetime.datetime(year=now.year, month=now.month, day=now.day,
                                       hour=int(form.begin_time.raw_data[0][:2]),
                                       minute=int(form.begin_time.raw_data[0][3:]))
        end_time = datetime.datetime(year=now.year, month=now.month, day=now.day,
                                     hour=int(form.end_time.raw_data[0][:2]),
                                     minute=int(form.end_time.raw_data[0][3:]))
        up_time = datetime.datetime(year=now.year, month=now.month, day=now.day,
                                    hour=int(form.up_time.raw_data[0][:2]),
                                    minute=int(form.up_time.raw_data[0][3:]))
        added_row = MainTable()
        added_row.n_route_id = route_data.id
        added_row.begin_time = begin_time
        added_row.end_time = end_time
        added_row.up_time = up_time
        added_row.n_st_id = form.st_number.raw_data[0]

        # добавляем запись в бд
        db_sess.add(added_row)
        db_sess.commit()
        return redirect('/')

    return render_template('add_edit_event.html', title='Добавить', form=form)


# функция возвращает список всех рейсов
@app.route('/routes', methods=['GET', 'POST'])
def routes():
    db_sess = db_session.create_session()
    data = db_sess.query(Routes).all()

    # проверяем наличия ключа в параметрах http-запроса (нужно для удаления событий)
    if 'route_id' in request.args.keys():
        id_row = request.args['route_id']
        db_sess.query(Routes).filter(Routes.id == id_row).delete()
        db_sess.commit()
        data = db_sess.query(Routes).all()

    return render_template("routes.html", data=enumerate(data))


# функция реализует форму редактирования выбранного рейса
@app.route('/edit_route', methods=['GET', 'POST'])
def edit_route():
    db_sess = db_session.create_session()
    form = AddEditRouteForm()
    id_row = 1
    # проверяем наличие параметра, содержащего id редактируемого события
    if 'route_id' in request.args.keys():
        id_row = request.args['route_id']
    data = db_sess.query(Routes).filter(Routes.id == int(id_row)).first()

    logos = os.listdir('static/img')
    logos.remove('nal_logo.png')
    logos.remove('nal_logo2.jpg')
    logos = [(i, i.split('.')[0]) for i in logos]

    form.route.data = data.route
    form.path_logo.choices = logos
    form.path_logo.data = data.path_logo
    form.airport.data = data.airport
    # обрабатываем нажатие на кнопку
    if form.validate_on_submit():
        # Проверяем название рейса на совпадение и имеющимися
        checking_data = db_sess.query(Routes).filter(Routes.route == form.route.raw_data[0],
                                                     Routes.id != id_row).all()
        if len(checking_data) != 0:
            return render_template('add_edit_route.html', title='Изменить', form=form,
                                   message="Рейс с таким названием уже существует")
        # Проверяем наличие файла с логотипом
        if not os.access(f'static/img/{form.path_logo.raw_data[0]}', os.F_OK):
            return render_template('add_edit_route.html', title='Изменить', form=form,
                                   message="Файл с логотипом не найден")
        edited_row = Routes()
        edited_row.id = id_row
        edited_row.route = form.route.raw_data[0]
        edited_row.path_logo = form.path_logo.raw_data[0]
        edited_row.airport = form.airport.raw_data[0]

        # удаляем старую запись и делаем новую
        db_sess.query(Routes).filter(Routes.id == id_row).delete()
        db_sess.commit()
        db_sess.add(edited_row)
        db_sess.commit()
        return redirect('/routes')

    return render_template('add_edit_route.html', title='Изменить', form=form)


# функция реализует форму добавления нового рейса
@app.route("/add_route", methods=['GET', 'POST'])
def add_route():
    db_sess = db_session.create_session()
    form = AddEditRouteForm()
    logos = os.listdir('static/img')
    logos.remove('nal_logo.png')
    logos.remove('nal_logo2.jpg')
    logos = [(i, i.split('.')[0]) for i in logos]

    form.path_logo.choices = logos
    form.submit.label.text = 'Добавить'
    # обрабатываем нажатие на кнопку
    if form.validate_on_submit():
        # Проверяем название рейса на совпадение и имеющимися
        checking_data = db_sess.query(Routes).filter(Routes.route == form.route.raw_data[0]).all()
        if len(checking_data) != 0:
            return render_template('add_edit_route.html', title='Изменить', form=form,
                                   message="Рейс с таким названием уже существует")
        # Проверяем наличие файла с логотипом
        if not os.access(f'static/img/{form.path_logo.raw_data[0]}', os.F_OK):
            return render_template('add_edit_route.html', title='Изменить', form=form,
                                   message="Файл с логотипом не найден")
        added_row = Routes()
        added_row.route = form.route.raw_data[0]
        added_row.path_logo = form.path_logo.raw_data[0]
        added_row.airport = form.airport.raw_data[0]

        # добавляем запись в бд
        db_sess.add(added_row)
        db_sess.commit()
        return redirect('/routes')

    return render_template('add_edit_route.html', title='Добавить', form=form)


# функция возвращает список всех табло
@app.route('/sts', methods=['GET', 'POST'])
def sts():
    db_sess = db_session.create_session()
    data = db_sess.query(Sts).all()

    # проверяем наличия ключа в параметрах http-запроса (нужно для удаления событий)
    if 'st_id' in request.args.keys():
        id_row = request.args['st_id']
        db_sess.query(Sts).filter(Sts.id == id_row).delete()
        db_sess.commit()
        data = db_sess.query(Sts).all()

    return render_template("sts.html", data=enumerate(data))


# функция реализует форму редактирования выбранного табло
@app.route('/edit_st', methods=['GET', 'POST'])
def edit_st():
    db_sess = db_session.create_session()
    form = AddEditStForm()
    id_row = 1
    # проверяем наличие параметра, содержащего id редактируемого события
    if 'st_id' in request.args.keys():
        id_row = request.args['st_id']
    data = db_sess.query(Sts).filter(Sts.id == int(id_row)).first()

    # список типов табло
    sts_type = [(0, '0 посадка'), ('1', '1 регистрация')]
    id_row = 1
    # проверяем наличие параметра, содержащего id редактируемого события
    if 'st_id' in request.args.keys():
        id_row = request.args['st_id']
    form.type.choices = sts_type
    form.remote_ip.data = data.remote_ip
    form.type.data = str(data.type)
    # обрабатываем нажатие на кнопку
    if form.validate_on_submit():
        # Проверяем ip табло на совпадение и имеющимися
        checking_data = db_sess.query(Sts).filter(Sts.remote_ip == form.remote_ip.raw_data[0],
                                                  Sts.id != id_row).all()
        if len(checking_data) != 0:
            return render_template('add_edit_st.html', title='Изменить', form=form,
                                   message="Табло с таким ip-адресом уже существует")
        # Проверка правильности формата ip-адреса
        if not correct_ip(form.remote_ip.raw_data[0]):
            return render_template('add_edit_st.html', title='Изменить', form=form,
                                   message="ip-адрес указан некорректно")
        edited_row = Sts()
        edited_row.id = id_row
        edited_row.remote_ip = form.remote_ip.raw_data[0]
        edited_row.type = form.type.raw_data[0]

        # удаляем старую запись и делаем новую
        db_sess.query(Sts).filter(Sts.id == id_row).delete()
        db_sess.commit()
        db_sess.add(edited_row)
        db_sess.commit()
        return redirect('/sts')

    return render_template('add_edit_st.html', title='Изменить', form=form)


# функция реализует форму добавления нового табло
@app.route("/add_st", methods=['GET', 'POST'])
def add_st():
    db_sess = db_session.create_session()
    form = AddEditStForm()
    form.submit.label.text = 'Добавить'
    sts_type = [(0, '0 посадка'), ('1', '1 регистрация')]
    form.type.choices = sts_type
    # обрабатываем нажатие на кнопку
    if form.validate_on_submit():
        # Проверяем ip табло на совпадение и имеющимися
        checking_data = db_sess.query(Sts).filter(Sts.remote_ip == form.remote_ip.raw_data[0]).all()
        if len(checking_data) != 0:
            return render_template('add_edit_st.html', title='Изменить', form=form,
                                   message="Табло с таким ip-адресом уже существует")
        # Проверка правильности формата ip-адреса
        if not correct_ip(form.remote_ip.raw_data[0]):
            return render_template('add_edit_st.html', title='Изменить', form=form,
                                   message="ip-адрес указан некорректно")
        added_row = Sts()
        added_row.remote_ip = form.remote_ip.raw_data[0]
        added_row.type = form.type.raw_data[0]

        # добавляем запись в бд
        db_sess.add(added_row)
        db_sess.commit()
        return redirect('/sts')

    return render_template('add_edit_st.html', title='Добавить', form=form)


# функция выбора файла логотипа
@app.route("/logo_add", methods=['GET', 'POST'])
def logo_choose():
    if request.method == 'POST':
        f = request.files['file']
        f.save('static/img/' + f.filename)
        return render_template('logo_add.html', title='Выбор логотипа', message='file uploaded successfully')
    return render_template('logo_add.html', title='Выбор логотипа')


# функция возвращает страницу текущего события табло, запросившего ее
@app.route("/st")
def st():
    db_sess = db_session.create_session()
    # узнаем ip-адрес клиента
    guest_ip = request.remote_addr
    state = 0
    data = []
    route_data = []
    # получаем данные о нашей стойке
    st_temp = db_sess.query(Sts).filter(Sts.remote_ip == guest_ip).first()
    # получаем данные для нашей стойки, если табло зарегистрировано
    if st_temp is not None:
        data = db_sess.query(MainTable).filter(MainTable.n_st_id == st_temp.id).all()
        state = 5
        if data is not None:
            for i in data:
                begin_time = i.begin_time
                end_time = i.end_time
                n_route_id = i.n_route_id
                # получаем данные о рейсе
                route_data = db_sess.query(Routes).filter(Routes.id == n_route_id).first()
                # определяем формат вывода на табло
                # вариант 1 - есть информация для вывода прямо сейчас, регистрация
                if begin_time <= datetime.datetime.now() <= end_time and st_temp.type == 1:
                    state = 1
                    data = i
                    break
                # вариант 2 - есть информация для вывода прямо сейчас, посадка
                elif begin_time <= datetime.datetime.now() <= end_time and st_temp.type == 0:
                    state = 2
                    data = i
                    break
                # вариант 3 - ожидается информация через 15 минут, только для табло регистрации
                elif begin_time <= datetime.datetime.now() + datetime.timedelta(minutes=15) <= end_time and \
                        st_temp.type == 1:
                    state = 3
                    data = i
                # вариант 4 - информация была 40 минут, только для табло регистрации
                elif begin_time <= datetime.datetime.now() - datetime.timedelta(minutes=40) <= end_time and \
                        st_temp.type == 1 and state != 3:
                    state = 4
                    data = i

    # получили всю инфу
    if state:
        return render_template("st.html", st_temp=st_temp, state=state, data=data,
                               route_data=route_data, time=datetime.datetime.now())
    else:
        return render_template("st.html", state=state)


# api для получения информации по текущему рейсу
@blueprint.route('/api/route_info/<string:route>', methods=['GET'])
def get_route_events(route):
    db_sess = db_session.create_session()
    route_object = db_sess.query(Routes).filter(Routes.route == route).first()
    result_events = db_sess.query(MainTable).filter(MainTable.n_route == route_object).all()
    if not result_events:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'events':
                [item.to_dict(only=('n_st_id', 'n_st.type', 'begin_time', 'end_time', 'up_time'))
                 for item in result_events]
        }
    )


# api для добавления нового события
@blueprint.route('/api/route_info', methods=['POST'])
def add_route_events():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['n_route_id', 'begin_time', 'end_time', 'up_time', 'n_st_id']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    adding_events = MainTable()
    adding_events.n_route_id = request.json['n_route_id']
    adding_events.begin_time = string_to_datetime(request.json['begin_time'])
    adding_events.end_time = string_to_datetime(request.json['end_time'])
    adding_events.up_time = string_to_datetime(request.json['up_time'])
    adding_events.n_st_id = request.json['n_st_id']

    db_sess.add(adding_events)
    db_sess.commit()
    return jsonify({'success': 'OK'})


def main():
    db_session.global_init("db/database.db")
    app.register_blueprint(route_info.blueprint)
    app.run()


if __name__ == '__main__':
    main()
