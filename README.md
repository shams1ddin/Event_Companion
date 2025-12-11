# Event Companion 1.5

Telegram event companion bot with in‑bot admin controls and a Django web admin. Supports multiple meetings, agenda, photos, geolocation, Wi‑Fi, PDF, participants, Q&A, and feedback. UI in three languages: English, Russian, Uzbek.

## Quick Start

- Install dependencies:

  ```bash
  pip install pyTelegramBotAPI django
  ```

- Set your bot token in `config.py` (obtain from `@BotFather`).
- Run the bot:

  ```bash
  python bot.py
  ```

  The bot initializes the SQLite database (`event_bot.db`) and starts polling.

- Run the Django web admin:

  ```bash
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver 0.0.0.0:8000
  ```

  Open `http://0.0.0.0:8000/admin/` and log in with the superuser.

## Project Files

- `config.py` — basic settings:
  - `BOT_TOKEN` — Telegram bot token
  - `ADMIN_PASSWORD` — password for in‑bot admin panel
  - `ADMIN_IDS` — list of administrator user IDs
  - `DATABASE_NAME` — SQLite file name (default `event_bot.db`)

- `database.py` — SQLite access helpers:
  - Initializes tables and indexes (`init_database`).
  - Tables:
    - `users` — bot users (language, name, phone, company, is_admin)
    - `meetings` — meetings: `name`, `location`, `date`, `wifi_*`, `latitude`, `longitude`, `deadline`, `ended`, `pdf_file_id`
    - `participants` — meeting participants (`meeting_id`, `user_id`)
    - `agenda` — agenda items: `title`, `start_time`, `end_time`, `description`
    - `agenda_alerts` — alerts subscriptions for agenda items
    - `questions` — user questions per meeting
    - `photos` — meeting photos (Telegram `file_id`)
    - `feedback` — user feedback (rating/text)
  - CRUD functions for users, meetings, participants, agenda, Wi‑Fi, geo, photos, PDF (`update_pdf`, `get_meeting_pdf`, `clear_pdf`), feedback.

- `texts.py` — localized UI texts:
  - `TEXTS` dict for all keys/buttons
  - `get_text(lang, key)` — fetches localized strings

- `keyboards.py` — Telegram inline keyboards:
  - User and admin menus
  - Meeting management: Wi‑Fi, photos, geo, agenda, PDF, finish/delete
  - Confirmation/action keyboards including `admin_pdf_*` and `admin_pdf_delete_confirm_*`

- `manage.py` — Django entry point.

- `bot.py` — main Telegram bot logic using `telebot`:
  - Initialization on start: `init_database()` and `init_feedback_table()` at `c:\Users\user\Desktop\дз\Event Companion 1.5\bot.py:1733-1735`
  - Handlers for commands and callbacks: admin panel, meetings, agenda, Wi‑Fi, geo, photos, PDF
  - Callback examples:
    - View PDF: `admin_pdf_{meeting_id}`
    - Add/Edit PDF: `admin_pdf_add_{id}`, `admin_pdf_edit_{id}`
    - Delete confirm: `admin_pdf_delete_confirm_yes_{id}`

- `webadmin/models.py` — Django models mapped to existing tables:
  - `managed = False` — models do not manage schema; they sit on top of existing SQLite tables
  - Models: `Meeting`, `Agenda`, `Photo`, `Question`, `Feedback`

- `webadmin/apps.py` — Django app configuration for `webadmin`.

- `webadmin/admin.py` — Django admin registrations:
  - `MeetingAdmin` with `AgendaInline` and `PhotoInline`
  - Separate admins for `Agenda`, `Photo`, `Question`, `Feedback`

- `webadmin/__init__.py` — package marker.

- `event_admin/wsgi.py`, `event_admin/asgi.py` — WSGI/ASGI entry points.

- `event_admin/urls.py` — Django routes (`/admin/`).

- `event_admin/settings.py` — Django settings:
  - `DATABASES['default']` points to the same `event_bot.db` via `config.DATABASE_NAME`
  - `INSTALLED_APPS` includes `webadmin`
  - `LANGUAGE_CODE = 'ru'`, `DEBUG = True` for development

- `event_admin/__init__.py` — package marker.

## Features

- Create/edit meetings via bot and web admin.
- Agenda management: add, edit, delete, subscribe to alerts.
- Meeting photos: upload via bot, view/edit via admin.
- Geolocation: set/clear meeting point.
- Wi‑Fi: store and edit SSID/password.
- PDF: store `file_id`, send to users, manage via admin.
- Participants: register users and list participants.
- Q&A and Feedback: collect and review by admin.

## Bot & Admin Working Together

- Bot and web admin share a single SQLite DB file `event_bot.db`.
- Changes in admin are immediately visible to the bot (and vice versa).
- `pdf_file_id` holds a Telegram File ID; uploading PDF is done through the bot.

## Security

- Do not commit a production bot token. Replace `BOT_TOKEN` in `config.py` and keep it private.
- For production, set `DJANGO_SECRET_KEY` and disable `DEBUG`.

## Commands

- Run bot: `python bot.py`
- Run admin server: `python manage.py runserver`
- Create superuser: `python manage.py createsuperuser`
- Apply admin migrations: `python manage.py migrate`

## Requirements

- Python 3.10+
- `pyTelegramBotAPI` (`telebot`)
- `Django 5.x`
