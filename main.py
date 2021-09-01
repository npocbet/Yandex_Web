import datetime
import os

from flask import Flask, render_template, redirect, request
from forms.add_edit_form import AddEditForm
from forms.add_edit_route_form import AddEditRouteForm
from forms.add_edit_st_form import AddEditStForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'


# функция возвращает список всех событий
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def events():

    # проверяем наличия ключа в параметрах http-запроса (нужно для удаления событий)
    if 'st_number' in request.args.keys():
        pass
    # тестовые значения табло
    data = [
        {'n_route': {'route': 'DP-194'},
         'n_st_id': 1,
         'n_st': {'type': 1},
         'begin_time':'2021-09-01 22:23:00.000000',
         'end_time':'2021-05-09 23:23:00.000000',
         'up_time':'2021-05-09 23:43:00.000000'
         },
        {'n_route': {'route': 'SU-1065'},
         'n_st_id': 2,
         'n_st': {'type': 1},
         'begin_time': '2021-09-01 22:43:00.000000',
         'end_time': '2021-05-09 23:43:00.000000',
         'up_time': '2021-05-09 23:53:00.000000'
         },
        {'n_route': {'route': 'DP-6902'},
         'n_st_id': 3,
         'n_st': {'type': 1},
         'begin_time': '2021-09-01 22:00:00.000000',
         'end_time': '2021-05-09 23:20:00.000000',
         'up_time': '2021-05-09 23:30:00.000000'
         }
    ]

    return render_template("events.html", data=enumerate(data))


# функция реализует форму редактирования выбранного события
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = AddEditForm()
    # список всех маршрутов - тестовые данные
    routes_list = [('DP-194', 'DP-194'), ('SU-1065', 'SU-1065'), ('DP-6902', 'DP-6902')]
    # список всех табло - тестовые данные
    sts_list = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
    id_row = 1
    # проверяем наличие параметра, содержащего id редактируемого события
    if 'st_number' in request.args.keys():
        id_row = request.args['st_number']
    form.route_number.choices = routes_list
    form.st_number.choices = sts_list
    # тестовые данные
    data = {'n_route': {'route': 'DP-194'},
         'n_st_id': 1,
         'n_st': {'type': 1},
         'begin_time':'2021-09-01 22:23:00.000000',
         'end_time':'2021-05-09 23:23:00.000000',
         'up_time':'2021-05-09 23:43:00.000000'
         }
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
        # здесь будем проверять пересечение с имеющимися событиями

        # тестовые данные
        route_data = {'n_route': {'route': 'DP-194'},
         'n_st_id': 1,
         'n_st': {'type': 1},
         'begin_time': '2021-09-01 22:23:00.000000',
         'end_time': '2021-05-09 23:23:00.000000',
         'up_time': '2021-05-09 23:43:00.000000'
         }

        # здесь будем менять запись БД, удаляя старую и добавляя новую

        return redirect('/')

    return render_template('add_edit_event.html', title='Изменить', form=form)


# функция реализует форму добавления нового события
@app.route("/add", methods=['GET', 'POST'])
def add():
    # список всех маршрутов - тестовые данные
    routes_list = [('DP-194', 'DP-194'), ('SU-1065', 'SU-1065'), ('DP-6902', 'DP-6902')]
    # список всех табло - тестовые данные
    sts_list = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')]
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
        # здесь будем проверять пересечение с имеющимися событиями

            # тестовые данные
        route_data = {'n_route': {'route': 'DP-194'},
                    'n_st_id': 1,
                    'n_st': {'type': 1},
                    'begin_time': '2021-09-01 22:23:00.000000',
                    'end_time': '2021-05-09 23:23:00.000000',
                    'up_time': '2021-05-09 23:43:00.000000'
                    }
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
        # здесь будем делать запись БД

        return redirect('/')

    return render_template('add_edit_event.html', title='Добавить', form=form)


# функция возвращает список всех рейсов
@app.route('/routes', methods=['GET', 'POST'])
def routes():
    # проверяем наличия ключа в параметрах http-запроса (нужно для удаления событий)
    if 'route_id' in request.args.keys():
        id_row = request.args['route_id']
        # тестовые данные
    data = [{'route': 'DP-194',
                      'path_logo': 'pobeda_logo.png',
                      'airport': 'Внуково'},
                {'route': 'SU-1065',
                 'path_logo': 'aeroflot.png',
                 'airport': 'Шереметево'},
                {'route': 'DP-6902',
                 'path_logo': 'pobeda_logo.png',
                 'airport': 'Шереметево'}
                ]

    return render_template("routes.html", data=enumerate(data))


# функция реализует форму редактирования выбранного рейса
@app.route('/edit_route', methods=['GET', 'POST'])
def edit_route():
    form = AddEditRouteForm()
    id_row = 1
    # проверяем наличие параметра, содержащего id редактируемого события
    if 'route_id' in request.args.keys():
        id_row = request.args['route_id']
    data = {'route': 'DP-194',
                      'path_logo': 'pobeda_logo.png',
                      'airport': 'Внуково'}

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
        # Здесь будем проверять название рейса на совпадение и имеющимися

        # здесь будем менять запись БД, удаляя старую и добавляя новую

        return redirect('/routes')

    return render_template('add_edit_route.html', title='Изменить', form=form)


# функция реализует форму добавления нового рейса
@app.route("/add_route", methods=['GET', 'POST'])
def add_route():
    form = AddEditRouteForm()
    logos = os.listdir('static/img')
    logos.remove('nal_logo.png')
    logos.remove('nal_logo2.jpg')
    logos = [(i, i.split('.')[0]) for i in logos]

    form.path_logo.choices = logos
    form.submit.label.text = 'Добавить'
    # обрабатываем нажатие на кнопку
    if form.validate_on_submit():
        # Здесь будем проверять название рейса на совпадение и имеющимися

        # здесь будем менять запись БД, удаляя старую и добавляя новую

        return redirect('/routes')

    return render_template('add_edit_route.html', title='Добавить', form=form)


# функция возвращает список всех табло
@app.route('/sts', methods=['GET', 'POST'])
def sts():
    data = [{'id': '1',
            'remote_ip': '172.16.2.3',
            'type': 1},
            {'id': '2',
             'remote_ip': '172.16.2.4',
             'type': 1},
            {'id': '3',
             'remote_ip': '127.0.0.1',
             'type': 0}]

    # проверяем наличия ключа в параметрах http-запроса (нужно для удаления событий)
    if 'st_id' in request.args.keys():
        # здесь будем удалять событие
        pass

    return render_template("sts.html", data=enumerate(data))


# функция реализует форму редактирования выбранного табло
@app.route('/edit_st', methods=['GET', 'POST'])
def edit_st():
    form = AddEditStForm()
    id_row = 1
    # проверяем наличие параметра, содержащего id редактируемого события
    if 'st_id' in request.args.keys():
        id_row = request.args['st_id']
    data = {'id': '1',
            'remote_ip': '172.16.2.3',
            'type': 1}

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
        # Здесь будем проверять ip табло на совпадение и имеющимися

        # Проверка правильности формата ip-адреса

        # Здесь будем проверять название рейса на совпадение и имеющимися

        # здесь будем менять запись БД, удаляя старую и добавляя новую

        return redirect('/sts')

    return render_template('add_edit_st.html', title='Изменить', form=form)


# функция реализует форму добавления нового табло
@app.route("/add_st", methods=['GET', 'POST'])
def add_st():
    form = AddEditStForm()
    form.submit.label.text = 'Добавить'
    sts_type = [(0, '0 посадка'), ('1', '1 регистрация')]
    form.type.choices = sts_type
    # обрабатываем нажатие на кнопку
    if form.validate_on_submit():
        # Здесь будем проверять ip табло на совпадение и имеющимися

        # Проверка правильности формата ip-адреса

        # Здесь будем проверять название рейса на совпадение и имеющимися

        # здесь будем добавлять новую запись в БД

        return redirect('/sts')

    return render_template('add_edit_st.html', title='Добавить', form=form)


# функция выбора файла логотипа
@app.route("/logo_add", methods=['GET', 'POST'])
def logo_choose():
    # здесь будем реализовано добавление логотипа

    return render_template('logo_add.html', title='Выбор логотипа')


# функция возвращает страницу текущего события табло, запросившего ее
@app.route("/st")
def st():
    # узнаем ip-адрес клиента
    guest_ip = request.remote_addr
    state = 0
    data = []
    route_data = []
    # получаем данные о нашей стойке тестовые данные
    st_temp = {'id': '3',
             'remote_ip': '127.0.0.1',
             'type': 0}
    # получаем данные для нашей стойки, если табло зарегистрировано тестовые данные
    if st_temp is not None:
        data = [{'n_route': {'route': 'DP-6902'},
         'n_st_id': 3,
         'n_st': {'type': 1},
         'begin_time': '2021-09-01 22:00:00.000000',
         'end_time': '2021-05-09 23:20:00.000000',
         'up_time': '2021-05-09 23:30:00.000000'
         }]
        state = 5
        if data is not None:
            for i in data:
                begin_time = i.begin_time
                end_time = i.end_time
                n_route_id = i.n_route_id
                # получаем данные о рейсе
                route_data = {'route': 'DP-6902',
                 'path_logo': 'pobeda_logo.png',
                 'airport': 'Шереметево'}
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


# Здесь будет api для получения информации по текущему рейсу

# Здесь будет api для добавления нового события

def main():
    app.run()


if __name__ == '__main__':
    main()
