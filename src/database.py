import sqlite3
import time


class Database:
    CONN = sqlite3.connect('server.db')
    CUR = CONN.cursor()

    def saveMessage(message: str, userID: int, channelID: int) -> None:
        '''saves message to MessageDB'''
        # called by server.py - saveMessage

        Database.CUR.execute('''INSERT INTO MessageDB (channel_id, user_id, timestamp, message) VALUES (?, ?, ?, ?)''', 
                             (channelID, userID, time.time(), message))


    def getMessage(channelID: int) -> list[tuple]:
        '''gets message from MessageDB based on channel id and return it to server.py'''
        # called by server.py - sendMessage

        Database.CUR.execute('''SELECT MessageDB.message WHERE channel_id = ? LIMIT 200''', (channelID,))
        return Database.CUR.fetchall()
        

    def changeProfile(userID: int, name: str) -> None:
        '''changes username in UserDB'''
        # called by server.py - updateProfile

        Database.CUR.execute('''UPDATE UserDB SET username = ? WHERE user_id = ?''', (name, userID))


    def addConversation(user1: int, user2: int) -> None:
        '''creates a new channel between user1 and user2'''
        # called by server.py - 

        Database.CUR.execute('''INSERT INTO ChannelDB (user1_id, user2_id, user1_display, user2_display) VALUES (?, ?, ?, ?)''',
                             (user1, user2, 1, 1))


    def hideConversation(channelID: int, user1: bool | None, user2: bool | None) -> None:
        '''change display status of user1 and/or user2'''
        # called by server.py - changeConversationVisibility

        # if user1 value is bool, change conversation display
        if user1 == True:
            Database.CUR.execute('''UPDATE ChannelDB SET user1_display = 1 WHERE channel_id = ?''', (channelID,))
        elif user1 == False:
            Database.CUR.execute('''UPDATE ChannelDB SET user1_display = 0 WHERE channel_id = ?''', (channelID,))

        # if user2 value is bool, change conversation display
        if user2 == True:
            Database.CUR.execute('''UPDATE ChannelDB SET user2_display = 1 WHERE channel_id = ?''', (channelID,))
        elif user2 == False:
            Database.CUR.execute('''UPDATE ChannelDB SET user2_display = 0 WHERE channel_id = ?''', (channelID,))

        # if both user display is set to 0 (false) delete the channel and corresponding messages
        Database.CUR.execute('''SELECT user1_display, user2_display, channel_id FROM ChannelDB WHERE user1_id = ? AND user2_id = ?''', (user1, user2))
        row = Database.CUR.fetchone()
        if row[0] == 0 and row[1] == 1:
            Database.deleteConversation(row[2])


    def deleteConversation(channelID: int) -> None:
        '''remove channel_id and associated messages from ChannelDB and MessageDB'''
        # called by hideConversationwhen both users decide to hide a conversation

        Database.CUR.execute('''DELETE FROM MessageDB WHERE channel_id = ?''', (channelID,))
        Database.CUR.execute('''DELETE FROM ChannelDB WHERE channel_id = ?''', (channelID))


    def handleLogin(username: str, password: str) -> tuple[int] | None:
        '''check if username and password matches records in UserDB
        returns the userID that corresponds with the username and password if records match, none if recores does not match'''
        # called by server.py - handleLogin

        Database.CUR.execute('''SELECT user_id FROM UserDB WHERE username = ? AND password = ?''', (username, password))
        return Database.CUR.fetchone()
    
    def onServerClose():
        '''on server close, commit all changes made during runtime and close the Database'''
        
        Database.CONN.commit()
        Database.CONN.close()


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