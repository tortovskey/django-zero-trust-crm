# KOSTY: описание проекта

KOSTY — учебная информационная система для учета клиентов и обработки заявок. В проекте показаны базовые меры защиты: Django authentication, CSRF, password hashing, RBAC, журналирование, демонстрационный MFA и элементы GDPR.

Это не production-ready система. MFA, доверенные устройства и GDPR-процессы реализованы как учебная демонстрация для курсовой работы.

## Быстрый запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Откройте `http://127.0.0.1:8000/`.

## Демо-аккаунты

`admin/admin12345`, `manager/manager12345`, `security/security12345`, `auditor/auditor12345`, `user/user12345`.

MFA-код для демонстрации: `123456`.
