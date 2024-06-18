import socket
import pickle
import tkinter
import time
import actionIDs

class MainGUI(tkinter.Tk):
    def __init__(self):
        self._userID = self.login()
        pass
    
    def login(self) -> int:
        '''Logs into an account and returns the user id'''
        pass
    
    def sendMessage(self) -> None:
        pass