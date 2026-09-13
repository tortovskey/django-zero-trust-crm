# Django Zero Trust CRM (KOSTY)

KOSTY — учебная защищенная информационная система управления клиентскими заявками с применением принципов Zero Trust Architecture и требований GDPR.

Проект сделан как запускаемый веб-прототип для защиты курсовой работы: авторизация, роли, SQLite-база, CRUD клиентов и заявок, журнал безопасности, демонстрационный MFA, GDPR-раздел, seed-данные и тесты.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Для Linux/Mac:

```bash
source venv/bin/activate
```

В текущем окружении Windows также можно запускать команды через `py`, например:

```bash
py manage.py runserver
```

## Тестовые пользователи

| Логин | Пароль | Роль |
| --- | --- | --- |
| `admin` | `admin12345` | Администратор |
| `manager` | `manager12345` | Менеджер |
| `security` | `security12345` | Специалист по безопасности |
| `auditor` | `auditor12345` | Аудитор |
| `user` | `user12345` | Обычный пользователь |

Для пользователей `admin`, `manager` и `security` включен учебный MFA. Код: `123456`.

## Реализовано

- регистрация, вход, выход и демонстрационный MFA;
- роли и RBAC-проверки на уровне Django views;
- CRUD клиентов с полями согласия на обработку данных;
- CRUD заявок со статусами, приоритетами, поиском и фильтрами;
- журнал событий безопасности и список условно доверенных устройств;
- GDPR-раздел: экспорт моих данных в JSON, запросы на удаление, политика хранения;
- seed-команда `python manage.py seed_data`;
- базовые Django tests.

## Документация

Подробные материалы находятся в папке `docs`:

- `docs/INSTALL.md`
- `docs/ARCHITECTURE.md`
- `docs/ZERO_TRUST.md`
- `docs/GDPR.md`
- `docs/ROLES.md`
- `docs/DATABASE.md`
- `docs/COURSEWORK_REPORT.md`


## Конфигурация

Параметры Django задаются через переменные окружения. Для локальной разработки можно ориентироваться на `.env.example`; сам `.env` в Git не добавляется. Значения по умолчанию предназначены только для локального запуска.

Файл `db.sqlite3` также не публикуется: демонстрационные данные создаются командой `python manage.py seed_data`.

## Тесты

```bash
python manage.py test
```

Проверяются ограничения доступа, создание заявки менеджером, запрет редактирования для аудитора, запись события безопасности при отказе и JSON-экспорт данных.
