import datetime
from requests import get, post

# для проверки
print(get('http://localhost:5000/api/route_info/N4-562').json())
print(get('http://localhost:5000/api/route_info/N4-563').json())

# для проверки добавления события
now = datetime.datetime.now()
begin_time = now
end_time = begin_time + datetime.timedelta(hours=3)
up_time = end_time + datetime.timedelta(minutes=40)
print(post('http://localhost:5000/api/route_info',
           json={'n_route_id': 1,
                 'begin_time': begin_time.strftime('%Y:%m:%d:%H:%M:%S'),
                 'end_time': end_time.strftime('%Y:%m:%d:%H:%M:%S'),
                 'up_time': up_time.strftime('%Y:%m:%d:%H:%M:%S'),
                 'n_st_id': 1}).json())
