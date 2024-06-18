import sqlite3
import time


class database:
    CUR = sqlite3.connect('server.db').cursor()

    def saveMessage(message: str, userID: int, channelID: int) -> None:
        '''saves message to MessageDB'''
        # called by server.py - saveMessage

        database.CUR.execute('''INSERT INTO MessageDB (channel_id, user_id, timestamp, message) VALUES (?, ?, ?, ?)''', 
                             (channelID, userID, time.time(), message))

    def getMessage(channelID: int) -> list[tuple]:
        '''gets message from MessageDB based on channel id and return it to server.py'''
        # called by server.py - sendMessage

        database.CUR.execute('''SELECT MessageDB.message WHERE channel_id = ?''', (channelID,))
        return database.CUR.fetchall()[:200]
        
    def changeProfile(userID: int, name: str) -> None:
        '''changes username in UserDB'''
        # called by server.py - updateProfile

        database.CUR.execute('''UPDATE UserDB SET username = ? WHERE user_id = ?''', (name, userID))

    def addConversation(user1: int, user2: int) -> None:
        '''creates a new channel between user1 and user2'''
        # called by server.py - 

        database.CUR.execute('''INSERT INTO ChannelDB (user1_id, user2_id, user1_display, user2_display) VALUES (?, ?, ?, ?)''',
                             (user1, user2, 1, 1))

    def hideConversation(channelID: int, user1: bool | None, user2: bool | None) -> None:
        '''change display status of user1 and/or user2'''
        # called by server.py - changeConversationVisibility

        if user1 == True:
            database.CUR.execute('''UPDATE ChannelDB SET user1_display = 1 WHERE channel_id = ?''', (channelID,))
        elif user1 == False:
            database.CUR.execute('''UPDATE ChannelDB SET user1_display = 0 WHERE channel_id = ?''', (channelID,))

        if user2 == True:
            database.CUR.execute('''UPDATE ChannelDB SET user2_display = 1 WHERE channel_id = ?''', (channelID,))
        elif user2 == False:
            database.CUR.execute('''UPDATE ChannelDB SET user2_display = 0 WHERE channel_id = ?''', (channelID,))

        database.CUR.execute('''SELECT * FROM ''')

    def deleteConversation(channelID: int) -> None:
        '''remove channel_id and associated messages from ChannelDB and MessageDB'''
        # called when both users decide to hide a conversation
        pass

    def handleLogin(username: str, password: str) -> int | None:
        '''check if username and password matches records in UserDB
        returns an int if records match, none if recores does not match'''
        # called by server.py - handleLogin
        pass


if __name__ == '__main__':
    conn = sqlite3.connect('server.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS MessageDB")
    cur.execute('''CREATE TABLE MessageDB
                    (message_id INTEGER NOT NULL PRIMARY KEY UNIQUE,
                    channel_id INTEGER,
                    user_id INTEGER,
                    timestamp REAL,
                    message TEXT)''')
    
    cur.execute("DROP TABLE IF EXISTS UserDB")
    cur.execute('''CREATE TABLE UserDB
                    (user_id NOT NULL PRIMARY KEY UNIQUE,
                    username TEXT,
                    last_login INTEGER,
                    password TEXT)''')
    
    cur.execute("DROP TABLE IF EXISTS ChannelDB")
    cur.execute('''CREATE TABLE ChannelDB
                    (channel_id NOT NULL PRIMARY KEY UNIQUE,
                    user1_id INTEGER,
                    user2_id INTEGER,
                    user1_display INTEGER,
                    user2_display INTEGER)''')