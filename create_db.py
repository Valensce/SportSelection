import sqlite3 as db

conn = db.connect('user_data.db')

conn.execute('''CREATE TABLE IF NOT EXISTS sports
                (sport_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL, 
                location TEXT NOT NULL, 
                teacher TEXT NOT NULL
                );''')

conn.execute('''CREATE TABLE IF NOT EXISTS Users 
                (user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                fullname TEXT NOT NULL, 
                username TEXT NOT NULL, 
                email TEXT UNIQUE NOT NULL,
                password TEXT
                );''') 

conn.execute('''CREATE TABLE IF NOT EXISTS student_sports
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            sport_id INTEGER
           
            );''')
                
conn.commit()
conn.close()