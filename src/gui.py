import socket
import tkinter as tk
import tkinter.messagebox as tkmb
import client

class MainGUI(tk.Toplevel):
    # TODO - continously request new message updates using client's receiveMessage func
    def __init__(self, master: tk.Tk):
        '''creates the main chat app window'''

        super.__init__(master)
        self._client = master.getClient()
        self._userID = master.getUserID()

        ### TODO (top priority)- add a LB widget to show all the past conversations the user had
        ### TODO - add a menu for changing username and registering a new uesr
        ### TODO (top priority) - add a button to delete conversations
        ### TODO - add a button to open a new conversation
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



    def requestMessage(self) -> None:
        '''gets called continuously to receive message from server'''
        pass



class chatGUI(tk.Toplevel):
    def __init__(self, master: tk.Toplevel, channel: int) -> None:
        pass



    def sendMessage(self, event) -> None:
        pass



    def receiveMessage(self) -> None:
        pass



class loginGUI(tk.Tk):
    def __init__(self) -> None:
        '''creates a window for the user to enter their username and password
           shows an error MessageBox if username and/or password does not match database records
           creates the main gui window if records match'''

        super().__init__()
        self.title("Login")
        self._usernameVar = tk.StringVar()
        self._passwordVar = tk.StringVar()
        
        tk.Label(self, text="Sign In", font=("Helvetica", "20")).grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(self, text="Username", font=("Helvetica", "12")).grid(row=1, column=0, padx=10)
        tk.Label(self, text="Password", font=("Helvetica", "12")).grid(row=2, column=0, padx=10)

        self._usernameEntry = tk.Entry(self, textvariable=self._usernameVar)
        self._passwordEntry = tk.Entry(self, textvariable=self._passwordVar)
        self._usernameEntry.grid(row=1, column=1, padx=10, pady=10)
        self._passwordEntry.grid(row=2, column=1, padx=10, pady=10)

        submitBtn = tk.Button(self, text="Login", font=("Helvetica", "15"), command=self.checkCredential).grid(row=3, column=0, columnspan=2, padx=10, pady=10)



    def checkCredential(self) -> None:
        # self._client = client.Client()

        self._usernameEntry.delete(0, tk.END)
        self._passwordEntry.delete(0, tk.END)

        self._userID = None
        if self._userID == None:
            tkmb.showerror("Error", "Login failed. Please check your username and password and try again")
        else:
            main = MainGUI(self)
            while main.winfo_exists():
                pass
            self.destroy()
            self.quit()



    def getUserID(self) -> int:
        return self._userID



    def getClient(self) -> socket.socket:
        return self._client
    

loginGUI().mainloop()