import sqlite3

conn = sqlite3.connect('wellbeing.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS moods (date TEXT, mood TEXT)''')