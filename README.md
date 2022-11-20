# Yatube соцсеть для блогеров

### Описание
Социальная сеть для публикации личных дневников. Создайте свою страницу,
переходите на страницы других пользователей, подписывайтесь на них, комментируйте их записи
***
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:kirefim/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
. venv/bin/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
cd yatube
```

```
python manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
