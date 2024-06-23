import sqlite3
import os

class Database:
    PATH = os.path.realpath(os.path.join(os.getcwd(), './data/server.db'))
    CONN = sqlite3.connect(PATH, check_same_thread=False)
    CUR = CONN.cursor()

    def saveMessage(message: str, userID: int, timestamp: float, channelID: int) -> None:
        '''saves message to MessageDB'''
        # called by server.py - saveMessage

        Database.CUR.execute('''INSERT INTO MessageDB (channel_id, user_id, timestamp, message) VALUES (?, ?, ?, ?)''', 
                             (channelID, userID, timestamp, message))
        Database.CONN.commit()

    

    def getChannelMessages(channelID: int) -> list[tuple[int, str]]:
        '''gets message from MessageDB based on channel id and return it to server.py'''
        # called by server.py - handleOpenConversation

        Database.CUR.execute('''SELECT user_id, message, FROM Message.DB WHERE channel_id = ? LIMIT 200''', (channelID,))
        return Database.CUR.fetchall()
        
        

    def getMessages(oldestTime: float) -> list[tuple]:
        '''return all messages until a given time'''

        Database.CUR.execute('''SELECT * FROM MessageDB WHERE timestamp > ?''', (oldestTime, ))
        return Database.CUR.fetchall()
        


    def changeProfile(userID: int, name: str) -> None:
        '''changes username in UserDB'''
        # called by server.py - updateProfile

        Database.CUR.execute('''UPDATE UserDB SET username = ? WHERE user_id = ?''', (name, userID))
        Database.CONN.commit()



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
        Database.CONN.commit()




    def hideConversation(channelID: int, userID: int, visibliity: bool) -> None:
        '''change display status of user1 and/or user2'''
        # called by server.py - changeConversationVisibility
        # 1 = True, 0 = False

        # get the entire row where channelID and userID matches
        row = Database.CUR.execute('''SELECT * FROM ChannelDB WHERE channel_id = ?''', (channelID,)).fetchone()
        if row[1] == userID: # if user1_id matches userID...
            if visibliity == True:
                Database.CUR.execute('''UPDATE ChannelDB SET user1_display = 1 WHERE channel_id = ?''', (channelID,))
            else:
                Database.CUR.execute('''UPDATE ChannelDB SET user1_display = 0 WHERE channel_id = ?''', (channelID,))
        else: # if user2_id matches userID...
            if visibliity == True:
                Database.CUR.execute('''UPDATE ChannelDB SET user2_display = 1 WHERE channel_id = ?''', (channelID,))
            else:
                Database.CUR.execute('''UPDATE ChannelDB SET user2_display = 0 WHERE channel_id = ?''', (channelID,))

        # if both users have their visibility of the channel as false, call deleteConversation()
        visibility = Database.CUR.execute('''SELECT user1_display, user2_display FROM ChannelDB WHERE channel_id = ?''', (channelID,)).fetchone()
        if visibility[0] == 0 and visibility[1] == 0:
            Database.deleteConversation(channelID)

        Database.CONN.commit()



    def deleteConversation(channelID: int) -> None:
        '''remove channel_id and associated messages from ChannelDB and MessageDB'''
        # called by hideConversationwhen both users decide to hide a conversation

        Database.CUR.execute('''DELETE FROM MessageDB WHERE channel_id = ?''', (channelID,))
        Database.CUR.execute('''DELETE FROM ChannelDB WHERE channel_id = ?''', (channelID,))



    def registerUser(username: str, password: str) -> bool:
        '''registers a new user in the database, returns if the operation is successful
           fails when someone else with the same username exists'''
        # called by server.py - handleRegistration
        
        # fetch one database entry that matches the passed in username
        check = Database.CUR.execute('''SELECT * FROM UserDB WHERE username = ?''', (username,)).fetchone()
        if check == None: # if nothing was fetched, put the username and password into the database
            Database.CUR.execute('''INSERT INTO UserDB (username, last_login, password) VALUES (?, ?, ?)''', (username, 0, password))
            Database.CONN.commit()
            return True
        else: # if something was fetched, someone already chose that username, fail the operation
            return False
    


    def getUserID(username: str) -> int | None:
        userID = Database.CUR.execute('''SELECT user_id FROM UserDB WHERE username = ?''', (username,)).fetchone()
        return userID[0]



    def handleLogin(username: str, password: str) -> int | None:
        '''check if username and password matches records in UserDB
        returns the userID that corresponds with the username and password if records match, none if recores does not match'''
        # called by server.py - handleLogin

        Database.CUR.execute('''SELECT user_id FROM UserDB WHERE username = ? AND password = ?''', (username, password))
        data = Database.CUR.fetchone()
        if data:
            return data[0]
        
        return None
    

    def onServerClose() -> None:
        '''on server close, close the Database'''
        
        Database.CONN.close()
        


    def getChannelUsers(channelID: int) -> tuple[int, int]:
        '''get the two user ids who's using the given channelID'''
        
        Database.CUR.execute('''
                             SELECT user1_id, user2_id FROM ChannelDB WHERE
                             channel_id = ?
                             ''', (channelID, ))
        return Database.CUR.fetchone()
    


    def getUsernames(userID: int) -> dict[str:int]:
        '''get the usernames of everyone who has conversed with the given userID'''

        # fetch all the user1_id and user2_ids tuples that match with userID
        userIDs = Database.CUR.execute('''SELECT user1_id, user2_id FROM ChannelDB WHERE user1_id = ? OR user2_id = ?''', (userID, userID)).fetchall()
        # filter to get the ids that is not the given userID
        # this means the ids we get are the ids that the given userID has conversed with
        ids = [id for idTuple in userIDs for id in idTuple if id != userID]
        # get the usernames of all the ids
        usernames = [Database.CUR.execute('''SELECT username, user_id FROM UserDB WHERE user_id = ?''', (id,)).fetchone() for id in ids]
        # return the list of usernames
        return dict(zip(usernames, ids))
    


    def getChannelID(user1ID: int, user2ID: int) -> int:
        '''get the channelID that matches with user1ID and user2ID'''

        return Database.CUR.execute('''SELECT channel_id FROM ChannelDB WHERE user1_id = ? AND user2_id = ?''', (user1ID, user2ID)).fetchone()[0]
    
    def setLastLogin(userID:int, lastLogin: float) -> None:
        '''set the last login time of a user'''

        Database.CUR.execute('''UPDATE UserDB SET last_login = ? WHERE user_id = ?''', (lastLogin, userID))

    def getLastLogin(userID: int) -> float:
        '''get teh last login time of a user'''

        return Database.CUR.execute('''SELECT last_login FROM UserDB WHERE user_id = ?''', (userID)).fetchone[0]



if __name__ == '__main__':
    conn = sqlite3.connect(Database.PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS MessageDB")
    cur.execute('''CREATE TABLE MessageDB
                    (message_id INTEGER NOT NULL PRIMARY KEY,
                    channel_id INTEGER,
                    user_id INTEGER,
                    timestamp REAL,
                    message TEXT)''')
    
    cur.execute("DROP TABLE IF EXISTS UserDB")
    cur.execute('''CREATE TABLE UserDB
                    (user_id INTEGER NOT NULL PRIMARY KEY,
                    username TEXT,
                    last_login REAL,
                    password TEXT)''')
    
    cur.execute("DROP TABLE IF EXISTS ChannelDB")
    cur.execute('''CREATE TABLE ChannelDB
                    (channel_id INTEGER NOT NULL PRIMARY KEY,
                    user1_id INTEGER,
                    user2_id INTEGER,
                    user1_display INTEGER,
                    user2_display INTEGER)''')