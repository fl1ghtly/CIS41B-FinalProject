import sqlite3


def saveMessage(message: str, userID: int, channelID: int) -> None:
    '''saves message to MessageDB'''
    # called by server.py - saveMessage
    pass

def getMessage(channelID: int) -> tuple:
    '''gets message from MessageDB based on channel id and return it to server.py'''
    # called by server.py - sendMessage
    pass

def changeProfile(userID: int, name: str) -> None:
    '''changes username in UserDB'''
    # called by server.py - updateProfile
    pass

def addConversation(user1: int, user2: int) -> None:
    # called by server.py - 
    pass

def hideConversation(channelID: int, userID: int) -> None:
    '''change user[]_display to 0 (false)'''
    # called by server.py - changeConversationVisibility
    pass

def deleteConversation(channelID: int) ->None:
    '''remove channel_id and associated messages from ChannelDB and MessageDB'''
    ## called when both users decide to hide a conversation
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
                    timestamp INTEGER,
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