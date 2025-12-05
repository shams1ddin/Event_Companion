# database.py
import sqlite3
from config import DATABASE_NAME
from datetime import datetime

def init_database():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'en',
                    name TEXT,
                    phone TEXT,
                    company TEXT,
                    is_admin INTEGER DEFAULT 0
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT,
                    date TEXT,
                    wifi_network TEXT,
                    wifi_password TEXT,
                    latitude REAL,
                    longitude REAL
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS participants (
                    meeting_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (meeting_id, user_id),
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS agenda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER,
                    title TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    description TEXT,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS agenda_alerts (
                    agenda_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (agenda_id, user_id),
                    FOREIGN KEY (agenda_id) REFERENCES agenda(id)
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER,
                    user_id INTEGER,
                    question TEXT,
                    date TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER,
                    file_id TEXT,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )''')
    try:
        c.execute("PRAGMA table_info(photos)")
        columns = [row[1] for row in c.fetchall()]
        if 'file_id' not in columns:
            c.execute("ALTER TABLE photos ADD COLUMN file_id TEXT")
    except Exception:
        pass

    try:
        c.execute("PRAGMA table_info(meetings)")
        columns = [row[1] for row in c.fetchall()]
        if 'latitude' not in columns:
            c.execute("ALTER TABLE meetings ADD COLUMN latitude REAL")
        if 'longitude' not in columns:
            c.execute("ALTER TABLE meetings ADD COLUMN longitude REAL")
        if 'deadline' not in columns:
            c.execute("ALTER TABLE meetings ADD COLUMN deadline TEXT")
        if 'ended' not in columns:
            c.execute("ALTER TABLE meetings ADD COLUMN ended INTEGER DEFAULT 0")
        if 'pdf_file_id' not in columns:
            c.execute("ALTER TABLE meetings ADD COLUMN pdf_file_id TEXT")
    except Exception:
        pass

    try:
        c.execute("PRAGMA table_info(agenda)")
        agenda_columns = [row[1] for row in c.fetchall()]
        if 'title' not in agenda_columns:
            c.execute("ALTER TABLE agenda ADD COLUMN title TEXT")
        if 'start_time' not in agenda_columns:
            c.execute("ALTER TABLE agenda ADD COLUMN start_time TEXT")
        if 'end_time' not in agenda_columns:
            c.execute("ALTER TABLE agenda ADD COLUMN end_time TEXT")
        # keep existing 'time' if present for backward compatibility
    except Exception:
        pass

    try:
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_agenda_alerts ON agenda_alerts(agenda_id, user_id)")
    except Exception:
        pass

    # Deduplicate participants and enforce uniqueness
    try:
        c.execute("DELETE FROM participants WHERE rowid NOT IN (SELECT MIN(rowid) FROM participants GROUP BY meeting_id, user_id)")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_participants_unique ON participants(meeting_id, user_id)")
    except Exception:
        pass

    conn.commit()
    conn.close()

# === USERS ===
def get_user(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(user_id, language='en'):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, language) VALUES (?, ?)", (user_id, language))
    conn.commit()
    conn.close()

def update_user_language(user_id, language):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
    conn.commit()
    conn.close()

def update_user_profile(user_id, name, phone, company):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET name = ?, phone = ?, company = ? WHERE user_id = ?", (name, phone, company, user_id))
    conn.commit()
    conn.close()

def set_admin(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_admin(user_id):
    user = get_user(user_id)
    return user[5] == 1 if user else False

def unset_admin(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# === MEETINGS ===
def create_meeting(name, location, date, lat=None, lon=None):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("""INSERT INTO meetings (name, location, date, latitude, longitude) 
                 VALUES (?, ?, ?, ?, ?)""", (name, location, date, lat, lon))
    meeting_id = c.lastrowid
    conn.commit()
    conn.close()
    return meeting_id

def update_location_geo(meeting_id, lat, lon):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET latitude = ?, longitude = ? WHERE id = ?", (lat, lon, meeting_id))
    conn.commit()
    conn.close()

def set_meeting_deadline(meeting_id, deadline_iso):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET deadline = ?, ended = 0 WHERE id = ?", (deadline_iso, meeting_id))
    conn.commit()
    conn.close()

def mark_meeting_ended(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET ended = 1 WHERE id = ?", (meeting_id,))
    conn.commit()
    conn.close()

def get_due_meetings(now_iso):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM meetings WHERE ended = 0 AND deadline IS NOT NULL AND deadline <= ?", (now_iso,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_meetings():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM meetings WHERE ended = 0 OR ended IS NULL ORDER BY id DESC")
    except Exception:
        c.execute("SELECT * FROM meetings ORDER BY id DESC")
    meetings = c.fetchall()
    conn.close()
    return meetings

def get_finished_meetings():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM meetings WHERE ended = 1 ORDER BY id DESC")
    except Exception:
        c.execute("SELECT * FROM meetings ORDER BY id DESC")
    meetings = c.fetchall()
    conn.close()
    return meetings

def get_meeting(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
    meeting = c.fetchone()
    conn.close()
    return meeting

def update_wifi(meeting_id, network, password):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET wifi_network = ?, wifi_password = ? WHERE id = ?", (network, password, meeting_id))
    conn.commit()
    conn.close()

def update_pdf(meeting_id, file_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET pdf_file_id = ? WHERE id = ?", (file_id, meeting_id))
    conn.commit()
    conn.close()

def get_meeting_pdf(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT pdf_file_id FROM meetings WHERE id = ?", (meeting_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def update_meeting_name(meeting_id, name):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET name = ? WHERE id = ?", (name, meeting_id))
    conn.commit()
    conn.close()

def update_meeting_date(meeting_id, date):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET date = ? WHERE id = ?", (date, meeting_id))
    conn.commit()
    conn.close()

def update_meeting_location(meeting_id, location):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET location = ? WHERE id = ?", (location, meeting_id))
    conn.commit()
    conn.close()

# === PARTICIPANTS ===
def add_participant(meeting_id, user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO participants (meeting_id, user_id) VALUES (?, ?)", (meeting_id, user_id))
    conn.commit()
    conn.close()

def get_participants(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("""SELECT u.user_id, u.name, u.phone, u.company 
                 FROM participants p 
                 JOIN users u ON p.user_id = u.user_id 
                 WHERE p.meeting_id = ?""", (meeting_id,))
    participants = c.fetchall()
    conn.close()
    return participants

def is_participant(meeting_id, user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM participants WHERE meeting_id = ? AND user_id = ?", (meeting_id, user_id))
    res = c.fetchone()
    conn.close()
    return res is not None

def remove_participant(meeting_id, user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM participants WHERE meeting_id = ? AND user_id = ?", (meeting_id, user_id))
    conn.commit()
    conn.close()

def get_participant_user_ids(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM participants WHERE meeting_id = ?", (meeting_id,))
    ids = c.fetchall()
    conn.close()
    return [row[0] for row in ids]

# === PHOTOS ===
def add_photo(meeting_id, file_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO photos (meeting_id, file_id) VALUES (?, ?)", (meeting_id, file_id))
    conn.commit()
    conn.close()

def get_photos(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT file_id FROM photos WHERE meeting_id = ?", (meeting_id,))
    photos = c.fetchall()
    conn.close()
    return [p[0] for p in photos]

# === QUESTIONS ===
def add_question(meeting_id, user_id, question):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO questions (meeting_id, user_id, question) VALUES (?, ?, ?)",
              (meeting_id, user_id, question))
    conn.commit()
    conn.close()

def get_questions(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE meeting_id = ? ORDER BY date DESC", (meeting_id,))
    questions = c.fetchall()
    conn.close()
    return questions

# === AGENDA (если захочешь потом добавить) ===
def get_agenda(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    try:
        c.execute("SELECT id, meeting_id, title, start_time, end_time, description FROM agenda WHERE meeting_id = ? ORDER BY start_time, id", (meeting_id,))
    except Exception:
        c.execute("SELECT id, meeting_id, title, start_time, end_time, description FROM agenda WHERE meeting_id = ? ORDER BY id", (meeting_id,))
    agenda = c.fetchall()
    conn.close()
    return agenda

def add_agenda_item(meeting_id, time, description):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO agenda (meeting_id, time, description) VALUES (?, ?, ?)", (meeting_id, time, description))
    except Exception:
        c.execute("INSERT INTO agenda (meeting_id, title, start_time, end_time, description) VALUES (?, ?, ?, ?, ?)", (meeting_id, None, time, None, description))
    conn.commit()
    conn.close()

def add_agenda_item_extended(meeting_id, title, start_time, end_time, description=None):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO agenda (meeting_id, title, start_time, end_time, description) VALUES (?, ?, ?, ?, ?)", (meeting_id, title, start_time, end_time, description or ''))
    conn.commit()
    conn.close()

def update_agenda_title(agenda_id, title):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE agenda SET title = ? WHERE id = ?", (title, agenda_id))
    conn.commit()
    conn.close()

def update_agenda_start_time(agenda_id, start_time):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE agenda SET start_time = ? WHERE id = ?", (start_time, agenda_id))
    conn.commit()
    conn.close()

def update_agenda_end_time(agenda_id, end_time):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE agenda SET end_time = ? WHERE id = ?", (end_time, agenda_id))
    conn.commit()
    conn.close()

def update_agenda_description(agenda_id, description):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE agenda SET description = ? WHERE id = ?", (description, agenda_id))
    conn.commit()
    conn.close()

def delete_agenda_item(agenda_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM agenda WHERE id = ?", (agenda_id,))
    conn.commit()
    conn.close()

def add_agenda_alert(agenda_id, user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO agenda_alerts (agenda_id, user_id) VALUES (?, ?)", (agenda_id, user_id))
    conn.commit()
    conn.close()

def remove_agenda_alert(agenda_id, user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM agenda_alerts WHERE agenda_id = ? AND user_id = ?", (agenda_id, user_id))
    conn.commit()
    conn.close()

def is_agenda_alerted(agenda_id, user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM agenda_alerts WHERE agenda_id = ? AND user_id = ?", (agenda_id, user_id))
    res = c.fetchone()
    conn.close()
    return res is not None

def get_agenda_alert_users(agenda_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT u.user_id, u.name, u.phone, u.company
        FROM agenda_alerts a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.agenda_id = ?
    """, (agenda_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_users():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    return users

# === ADMIN: DELETE MEETING ===
def delete_meeting(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM participants WHERE meeting_id = ?", (meeting_id,))
    c.execute("DELETE FROM photos WHERE meeting_id = ?", (meeting_id,))
    c.execute("DELETE FROM questions WHERE meeting_id = ?", (meeting_id,))
    c.execute("DELETE FROM agenda WHERE meeting_id = ?", (meeting_id,))
    c.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
    conn.commit()
    conn.close()

# === FEEDBACK ===
def init_feedback_table():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER,
                    user_id INTEGER,
                    rating TEXT,
                    feedback TEXT,
                    date TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )''')
    conn.commit()
    conn.close()

def add_feedback(meeting_id, user_id, rating, feedback=None):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO feedback (meeting_id, user_id, rating, feedback) VALUES (?, ?, ?, ?)", (meeting_id, user_id, rating, feedback))
    conn.commit()
    conn.close()

def get_feedback_for_meeting(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id, rating, feedback, date FROM feedback WHERE meeting_id = ? ORDER BY date DESC", (meeting_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# === ADMIN UTIL ===
def clear_wifi(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET wifi_network = NULL, wifi_password = NULL WHERE id = ?", (meeting_id,))
    conn.commit()
    conn.close()

def clear_photos(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM photos WHERE meeting_id = ?", (meeting_id,))
    conn.commit()
    conn.close()

def clear_agenda(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM agenda WHERE meeting_id = ?", (meeting_id,))
    conn.commit()
    conn.close()

def clear_geo(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET latitude = NULL, longitude = NULL WHERE id = ?", (meeting_id,))
    conn.commit()
    conn.close()

def clear_pdf(meeting_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE meetings SET pdf_file_id = NULL WHERE id = ?", (meeting_id,))
    conn.commit()
    conn.close()
