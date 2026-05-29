import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        age INTEGER,
        weight REAL,
        height REAL,
        goal TEXT DEFAULT 'maintain',
        daily_target INTEGER DEFAULT 2000
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        calories INTEGER NOT NULL,
        protein REAL DEFAULT 0,
        carbs REAL DEFAULT 0,
        fats REAL DEFAULT 0,
        meal_type TEXT,
        date TEXT DEFAULT CURRENT_DATE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        duration INTEGER NOT NULL,
        calories_burned INTEGER NOT NULL,
        date TEXT DEFAULT CURRENT_DATE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS weight_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        weight REAL NOT NULL,
        date TEXT DEFAULT CURRENT_DATE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password, age, weight, height, goal, target):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name,email,password,age,weight,height,goal,daily_target) VALUES (?,?,?,?,?,?,?,?)",
                  (name, email, hash_password(password), age, weight, height, goal, target))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?",
              (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def add_meal(user_id, name, calories, protein, carbs, fats, meal_type):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("INSERT INTO meals (user_id,name,calories,protein,carbs,fats,meal_type) VALUES (?,?,?,?,?,?,?)",
              (user_id, name, calories, protein, carbs, fats, meal_type))
    conn.commit()
    conn.close()

def get_today_meals(user_id):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("SELECT * FROM meals WHERE user_id=? AND date=DATE('now')", (user_id,))
    meals = c.fetchall()
    conn.close()
    return meals

def get_week_meals(user_id):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("SELECT date, SUM(calories) FROM meals WHERE user_id=? AND date >= DATE('now', '-7 days') GROUP BY date ORDER BY date", (user_id,))
    data = c.fetchall()
    conn.close()
    return data

def delete_meal(meal_id):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("DELETE FROM meals WHERE id=?", (meal_id,))
    conn.commit()
    conn.close()

def add_exercise(user_id, name, duration, calories_burned):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("INSERT INTO exercises (user_id,name,duration,calories_burned) VALUES (?,?,?,?)",
              (user_id, name, duration, calories_burned))
    conn.commit()
    conn.close()

def get_today_exercises(user_id):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("SELECT * FROM exercises WHERE user_id=? AND date=DATE('now')", (user_id,))
    exercises = c.fetchall()
    conn.close()
    return exercises

def log_weight(user_id, weight):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("INSERT INTO weight_log (user_id, weight) VALUES (?,?)", (user_id, weight))
    conn.commit()
    conn.close()

def get_weight_history(user_id):
    conn = sqlite3.connect('nutricam.db')
    c = conn.cursor()
    c.execute("SELECT date, weight FROM weight_log WHERE user_id=? ORDER BY date DESC LIMIT 30", (user_id,))
    data = c.fetchall()
    conn.close()
    return data