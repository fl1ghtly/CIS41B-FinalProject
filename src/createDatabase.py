import sqlite3

conn = sqlite3.connect('server.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE MessageDB
                (message_id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                channel_id INTEGER,
                user_id INTEGER,
                timestamp INTEGER,
                message TEXT)''')
cur.execute('''CREATE TABLE UserDB
                (user_id NOT NULL PRIMARY KEY UNIQUE
                username TEXT
                last_login INTEGER
                password TEXT)''')
cur.execute('''CREATE TABLE ChannelDB
                (channel_id NOT NULL PRIMARY KEY UNIQUE
                user1_id INTEGER
                user2_id INTEGER
                user1_display INTEGER
                user2_display INTEGER)''')