Проект системы информационных табло для малых аэропортов

Для запуска проекта необходимо установить модули flask, SQLAlchemy, Flask-WTF, Werkzeugб
WTForms, SQLAlchemy-serializer, requests


pip install flask
pip install SQLAlchemy
pip install Flask-WTF
pip install Werkzeug
pip install WTForms
pip install SQLAlchemy-serializer
pip install requests

либо воспользоваться файлом requirements.txt

Описание системы

Система состоит из сервера на фласк, клиентов - информационных табло, представляющих собой
экраны, имеющими сетевые интерфейсы, модули браузера, настраиваемого на веб-страницу,
и функцией ее авто обновления. Предполагается размещение в закрытой и защищенной сети, поэтому табло
регистрируются в системе простым добавлением их ip-адреса (он должен быть статическим) в соответствующую
таблицу БД. Оператор имеет возможность редактирования таблицы событий (регистрации или посадки
на соответствующий рейс с указанием номера табло для отображения). Также в системе реализованы 2
api для добавления событий и получения информации по конкретному рейсу.

Информация для тестирования:
1. Для тестирования таблицы событий (работа оператора) переходим на главную страницу по ссылке (127.0.0.1:5000/) или
(127.0.0.1:5000/index), на которой видим все имеющиеся события, можем их удалять, редактировать и добавлять новые, но
нужно учитывать ряд ограничений: 
а. у каждого события есть поля "Начало регистрации/посадки", "Окончание регистрации/посадки" и "Время вылета".
Второе должно быть позже первого, третье - позже второго.
б. события для одного и того же табло не могут накладываться друг на друга. Исключение - начало одного события
может совпадать с окончанием другого.
2. Форма добавления/редактирования содержит выпадающие списки рейсов и табло, уже внесенные в БД.
3. Для тестирования режима "табло" необходимо в п.1 создать события для табло с номером 7 (привязано к адресу 127.0.0.1).
Перед отображением информации происходит поиск наиболее актуального события для табло: в первую очередь ищем, событие,
которое "происходит" сейчас, т.е. текущее время между временем начала события и временем его окончания, затем событие, 
которое должно начаться в ближайшие 15 минут, далее — событие закончившееся в течение последних 40 минут. Наконец,
если актуальных событий найти не удалось — просто показываем логотип.
4. Для тестирования api - см. файл test.py
