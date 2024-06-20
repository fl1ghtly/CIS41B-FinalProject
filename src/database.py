import sqlite3
import time


class Database:
    CONN = sqlite3.connect('server.db')
    CUR = CONN.cursor()

    def saveMessage(message: str, userID: int, timestamp: float, channelID: int) -> None:
        '''saves message to MessageDB'''
        # called by server.py - saveMessage

        Database.CUR.execute('''INSERT INTO MessageDB (channel_id, user_id, timestamp, message) VALUES (?, ?, ?, ?)''', 
                             (channelID, userID, timestamp, message))

    

    def getChannelMessages(channelID: int) -> list[tuple]:
        '''gets message from MessageDB based on channel id and return it to server.py'''
        # called by server.py - sendMessage

        Database.CUR.execute('''SELECT MessageDB.message WHERE channel_id = ? LIMIT 200''', (channelID,))
        return Database.CUR.fetchall()
        
        

    def getMessages(oldestTime: float) -> list[tuple]:
        '''return all messages until a given time'''

        Database.CUR.execute('''SELECT * FROM MessageDB WHERE timestamp > ?''', (oldestTime, ))
        return Database.CUR.fetchall()
        


    def changeProfile(userID: int, name: str) -> None:
        '''changes username in UserDB'''
        # called by server.py - updateProfile

        Database.CUR.execute('''UPDATE UserDB SET username = ? WHERE user_id = ?''', (name, userID))



    def getProfiles() -> list[tuple]:
        '''return all profiles'''
        # called by server.py - sendProfiles
        
        Database.CUR.execute('''SELECT user_id, username FROM UserDB''')
        return Database.CUR.fetchall()
    


    def addConversation(user1: int, user2: int) -> None:
        '''creates a new channel between user1 and user2'''
        # called by server.py - 

        Database.CUR.execute('''INSERT INTO ChannelDB (user1_id, user2_id, user1_display, user2_display) VALUES (?, ?, ?, ?)''',
                             (user1, user2, 1, 1))




    def hideConversation(channelID: int, userID: int, visibliity: bool) -> None:
        '''change display status of user1 and/or user2'''
        # called by server.py - changeConversationVisibility
        # 1 = True, 0 = False

        row = Database.CUR.execute('''SELECT * FROM ChannelDB WHERE channel_id = ? AND (user1_id = ? OR user2_id = ?)''', (channelID, userID, userID)).fetchone()
        if row[1] == userID:
            if visibliity == True:
                Database.CUR.execute('''UPDATE ChannelDB SET user1_display = 1 WHERE channel_id = ?''', (channelID,))
            else:
                Database.CUR.execute('''UPDATE ChannelDB SET user1_display = 0 WHERE channel_id = ?''', (channelID,))
        else:
            if visibliity == True:
                Database.CUR.execute('''UPDATE ChannelDB SET user2_display = 1 WHERE channel_id = ?''', (channelID,))
            else:
                Database.CUR.execute('''UPDATE ChannelDB SET user2_display = 0 WHERE channel_id = ?''', (channelID,))



    def deleteConversation(channelID: int) -> None:
        '''remove channel_id and associated messages from ChannelDB and MessageDB'''
        # called by hideConversationwhen both users decide to hide a conversation

        Database.CUR.execute('''DELETE FROM MessageDB WHERE channel_id = ?''', (channelID,))
        Database.CUR.execute('''DELETE FROM ChannelDB WHERE channel_id = ?''', (channelID))



    def registerUser(username: str, password: str) -> bool:
        '''registers a new user in the database, returns if the operation is successful
           fails when someone else with teh same user name exists'''
        # called by server.py - handleRegistration
        
        check = Database.CUR.execute('''SELECT * FROM UserDB WHERE username = ?''', (username))
        if check == None:
            return False
        else:
            Database.CUR.execute('''INSERT INTO UserDB (username, last_login, password) VALUES (?, ?, ?, ?)''', (username, 0, password))
            return True
    


    def getUserID(username: str) -> int:
        userID = Database.CUR.execute('''SELECT user_id FROM UserDB WHERE username = ?''', (username,)).fetchone()
        return userID[0]



    def handleLogin(username: str, password: str) -> int | None:
        '''check if username and password matches records in UserDB
        returns the userID that corresponds with the username and password if records match, none if recores does not match'''
        # called by server.py - handleLogin

        Database.CUR.execute('''SELECT user_id FROM UserDB WHERE username = ? AND password = ?''', (username, password))
        return Database.CUR.fetchone()[0]
    


    def onServerClose():
        '''on server close, commit all changes made during runtime and close the Database'''
        
        Database.CONN.commit()
        Database.CONN.close()
        


    def getChannelUsers(channelID: int) -> tuple[int, int]:
        '''get the two user ids who's using the given channelID'''

        Database.CUR.execute('''
                             SELECT user1_id, user2_id FROM ChannelDB WHERE
                             channel_id = ?
                             ''', (channelID, ))
        return Database.CUR.fetchone()



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