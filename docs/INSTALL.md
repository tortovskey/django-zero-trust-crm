# Установка

## Требования

- Python 3.12+.
- SQLite используется встроенно.
- Зависимости из `requirements.txt`.

## Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Если команда `python` указывает на Microsoft Store stub, используйте:

```bash
py manage.py runserver
```

## Linux/Mac

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Проверка

```bash
python manage.py test
```
