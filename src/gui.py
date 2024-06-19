import tkinter
from database import database

class MainGUI(tkinter.Tk):
    # TODO continously request new message updates
    def __init__(self):
        # calls loginGUI
        pass

    def openChat(self, event) -> None:
        '''opens a new chatGUI when user clicks on a LB item'''
        pass

    def removeChat(self) -> None:
        '''removes a conversation'''
        pass

    def changeNickname(self) -> None:
        '''changes the user's nickname'''
        pass

    def createUser(self) -> None:
        '''creates a new user in the system'''
        pass

    def createChat(self) -> None:
        '''creates a new chat channel with another user'''
        pass

class chatGUI(tkinter.Toplevel):
    def __init__(self, channel: int) -> None:
        pass

    def sendMessage(self, event) -> None:
        pass


class loginGUI(tkinter.Toplevel):
    def __init__(self) -> None:
        '''creates a new window for the user to enter their username and password
           shows an error MessageBox if username and/or password does not match database records'''
        # called by MainGui - openChat()
        pass

    def getUserID(self) -> int:
        pass
