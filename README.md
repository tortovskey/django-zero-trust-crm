# Django Zero Trust CRM (KOSTY)

KOSTY is an educational CRM prototype for managing customers and service requests.
It explores Zero Trust principles and GDPR-related privacy workflows through
role-based access, security logging, demonstration MFA, and data controls.

The application includes authentication, roles, a SQLite database, customer and
request management, security events, seed data, and tests.

## Quick start

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

On Linux or macOS, activate the environment with:

```bash
source venv/bin/activate
```

On Windows, you can also use the Python launcher, for example:

```powershell
py manage.py runserver
```

## Demo accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `admin12345` | Administrator |
| `manager` | `manager12345` | Manager |
| `security` | `security12345` | Security specialist |
| `auditor` | `auditor12345` | Auditor |
| `user` | `user12345` | Standard user |

Demonstration MFA is enabled for `admin`, `manager`, and `security`.
The demo code is `123456`.

## Features

- Registration, sign-in, sign-out, and demonstration MFA.
- Roles and view-level RBAC checks.
- Customer CRUD operations with data-processing consent fields.
- Service requests with statuses, priorities, search, and filtering.
- Security event logging and a demonstration trusted-device list.
- Privacy workflows: JSON data export, deletion requests, and retention policy information.
- Seed data through `python manage.py seed_data`.
- Basic Django tests.

## Documentation

Additional material is available in `docs`:

- `docs/INSTALL.md`
- `docs/ARCHITECTURE.md`
- `docs/ZERO_TRUST.md`
- `docs/GDPR.md`
- `docs/ROLES.md`
- `docs/DATABASE.md`
- `docs/COURSEWORK_REPORT.md`

## Configuration

Django settings are supplied through environment variables. Use `.env.example`
as a reference for local development; the actual `.env` file is excluded from Git.
Default values are intended for local use only.

The repository also excludes `db.sqlite3`. Create demonstration data with
`python manage.py seed_data`.

## Tests

```bash
python manage.py test
```

The tests cover access restrictions, manager-created requests, auditor edit
restrictions, security logging on denied access, and JSON data export.
