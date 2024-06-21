import socket
import tkinter as tk
import tkinter.messagebox as tkmb
import client

class MainGUI(tk.Toplevel):
    # TODO - continously request new message updates using client's receiveMessage func
    def __init__(self, master: tk.Tk, connection: client.Client, userID: int, username: str):
        '''creates the main chat app window'''

        # create instance variables
        super.__init__(master)
        self.title("App")
        self._client = connection
        self._userID = userID
        self._username = username

        # create labels to welcome the user 
        tk.Label(self, text=f"Welcome {self._username}", font=("Courier New", "20", "bold")).grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(self, text="Past conversations", font=("Courier New", "12")).grid(row=1, column=0, padx=10, pady=10)

        # create frame to grid listbox and scrollbar
        F1 = tk.Frame(self)

        # create scrollbar widget for listbox widget
        S = tk.Scrollbar(F1)
        S.grid(row=0, column=1, sticky='ns')

        # create listbox to display past conversations
        D = self._client.receiveUsernames()
        usernames = D.values()
        LB = tk.Listbox(F1, height=10, width=20, yscrollcommand=S.set)
        LB.insert(tk.END, *usernames)
        LB.configure(font=("Courier New", "15"))
        LB.bind("<<ListboxSelect>>", lambda: self._openChat(LB))
        LB.grid(row=0, column=0)
        # config scrollbar together with listbox
        S.config(command=LB.yview)
        # grid frame
        F1.grid(row=2, column=0, padx=10, pady=10)

        # create frame to grid two buttons
        F2 = tk.Frame(self)

        # create button to delete chat and open a new chat
        tk.Button(F2, text="Delete Chat", fg="red", command=self._openChat, font=("Courier New", "12")).grid(row=0, pady=10)
        tk.Button(F2, text="New Chat", fg= "blue", command=self._removeChat, font=("Courier New", "12")).grid(row=1, pady=10)
        # grid frame
        F2.grid(row=2, column=1, padx=20)

        # create menu for changing nickname and making new account
        menu = tk.Menu(self)
        settings = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Settings", menu=settings)
        settings.add_command(label="Edit Nickname", command=self._changeNickname)
        settings.add_command(label="Register New Account", command=self._createUser)
        self.config(menu=menu)



    def _openChat(self, event, LB: tk.Listbox, D: dict[str:int]) -> None:
        '''opens a new chatGUI when user clicks on a LB item'''
        user2 = LB.get(LB.curselection())
        user2ID = D[user2]
        



    def _removeChat(self) -> None:
        '''removes a conversation'''
        pass



    def _createChat(self) -> None:
            '''creates a new chat channel with another user'''
            pass



    def _changeNickname(self) -> None:
        '''changes the user's nickname'''
        pass



    def _createUser(self) -> None:
        '''creates a new user in the system'''
        pass



    def _requestMessage(self) -> None:
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
        self._client = client.Client()
        self._client.login(self._usernameVar.get(), self._passwordVar.get())

        self._userID = self._client.getUserID()
        if self._userID == None:
            tkmb.showerror("Error", "Login failed. Please check your username and password and try again")
        else:
            main = MainGUI(self, self._client, self._userID, self._usernameVar.get())

            self._usernameEntry.delete(0, tk.END)
            self._passwordEntry.delete(0, tk.END)

            self.wait_window(main)
            self.destroy()
            self.quit()



    def getUserID(self) -> int:
        return self._userID



    def getClient(self) -> socket.socket:
        return self._client
    
    
    
    def getUsername(self) -> str:
        return self._usernameVar.get()
    

loginGUI().mainloop()