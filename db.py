import sqlite3


#=================================================================================================================
# Регистрация и инициализация

def init_db():
    conn = sqlite3.connect('dating.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        profile_key integer PRIMARY KEY UNIQUE,
        user_id INTEGER UNIQUE,
        user_name TEXT,
        user_profile_name TEXT,
        user_age INTEGER,
        user_gender TEXT,
        user_city TEXT,
        user_course INTEGER,
        user_direction INTEGER,
        profile_text TEXT,
        profile_media TEXT,
        user_reports INTEGER
        )
        ''')

    conn.commit()
    conn.close()


def check_registred(user_id):
    conn = sqlite3.connect('dating.db')
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM profiles WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()
    conn.close()
    is_registered = True
    if existing_user is None:
        is_registered = False
    return is_registered

#=================================================================================================================
# Геттеры и сеттеры

def get_profile(user_id):
    conn = sqlite3.connect('dating.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    user_profile = cursor.fetchone()
    conn.close()

    if user_profile:
        # Преобразуем строку в словарь
        return dict(user_profile)
    else:
        return None

def set_profile(user_id, user_name, user_profile_name, user_age, user_gender, user_direction, user_course, user_city, profile_text, profile_media):
    conn = sqlite3.connect('dating.db')
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO profiles (user_id, user_name, user_profile_name, user_age, user_gender, user_city, user_course, user_direction, profile_text, profile_media, user_reports)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, user_name, user_profile_name, user_age, user_gender, user_city, user_course, user_direction, profile_text, profile_media, 0)
                   )

    conn.commit()
    conn.close()

def set_media(user_id, new_media):
    conn = sqlite3.connect('dating.db')
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE profiles
    SET profile_media=?
    WHERE user_id=?
    """, (user_id, new_media))

    conn.commit()
    conn.close()

def set_name(user_id, new_name):
    conn = sqlite3.connect('dating.db')
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE profiles
    SET user_profile_name=?
    WHERE user_id=?
    """, (new_name, user_id))

    conn.commit()
    conn.close()

def set_direction(user_id, new_direction):
    conn = sqlite3.connect('dating.db')
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE profiles
    SET user_direction=?
    WHERE user_id=?
    """, (new_direction, user_id))

    conn.commit()
    conn.close()

def set_course(user_id, new_course):
    conn = sqlite3.connect('dating.db')
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE profiles
    SET user_course=?
    WHERE user_id=?
    """, (new_course, user_id))

    conn.commit()
    conn.close()