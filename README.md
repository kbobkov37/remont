# Remont

Django-проект с регистрацией пользователей, панелью управления и двухфакторной аутентификацией (TOTP).

Подробное ТЗ проекта: [docs/TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md)

## Возможности

- Регистрация: логин, пароль, ФИО, email, телефон
- Вход с 2FA (Google Authenticator, Authy и др.)
- Панель пользователя `/accounts/dashboard/`
- Django Admin с 2FA для сотрудников `/admin/`

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cd remont
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## URL

| Путь | Описание |
|------|----------|
| `/accounts/register/` | Регистрация |
| `/accounts/login/` | Вход |
| `/accounts/setup-2fa/` | Настройка 2FA |
| `/accounts/dashboard/` | Панель |
| `/admin/` | Админка Django |

## Стек

- Django 6
- django-otp (TOTP + резервные коды)
- SQLite (для разработки)
