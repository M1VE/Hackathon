# Локальный запуск без PostgreSQL команды



Команда использует свою PostgreSQL. Чтобы не ломать их настройки, у тебя локально включается SQLite через `.env`:



```env

USE_SQLITE=True

```



Это меняет только твою локальную БД (`db.sqlite3`). Файлы бэкенда для PostgreSQL остаются как есть.



## Быстрый старт



```bash

cd Hackathon

python -m pip install -r requirements.txt

python manage.py migrate

python manage.py seed_local_demo

python manage.py runserver

```



Сайт: http://127.0.0.1:8000/



## Как войти



### Обычный пользователь (сайт)



Страница: http://127.0.0.1:8000/login/



| Роль        | Email                   | Пароль    |

|-------------|-------------------------|-----------|

| Участник    | participant@demo.local  | demo1234  |

| Ментор      | mentor@demo.local       | demo1234  |

| Организатор | organizer@demo.local    | demo1234  |



После входа откроется личный кабинет по роли.



### Админ (Django Admin)



- URL: http://127.0.0.1:8000/admin/

- Email: `admin@demo.local`

- Пароль: `admin1234`



Либо создай своего суперпользователя:



```bash

python manage.py createsuperuser

```



### Регистрация вручную



http://127.0.0.1:8000/register/ — нужен университет в списке (после `seed_local_demo` будет Demo University).



## Важно для команды



- Не коммить `db.sqlite3`, если не договорились об этом.

- Не меняй `USE_SQLITE` в общем `.env` репозитория — держи локально.

- Команда `seed_local_demo` безопасна: она просто не запускается, если `USE_SQLITE=False`.

