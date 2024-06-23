import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.scrolledtext as st
import client
import time

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
        self._nameLabel = tk.Label(self, text=f"Welcome {self._username}", font=("Courier New", "20", "bold"))
        self._nameLabel.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(self, text="Past conversations", font=("Courier New", "12")).grid(row=1, column=0, padx=10, pady=10)

        # create frame to grid listbox and scrollbar
        F1 = tk.Frame(self)

        # create scrollbar widget for listbox widget
        S = tk.Scrollbar(F1)
        S.grid(row=0, column=1, sticky='ns')

        # create listbox to display past conversations
        self._usernamesDict: dict[str,int] = self._client.receiveUsernames()
        usernames = self._usernamesDict.keys()
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
        tk.Button(F2, text="Delete Chat", fg="red", command=lambda: self._removeChat(LB, self._usernamesDict), font=("Courier New", "12")).grid(row=0, pady=10)
        tk.Button(F2, text="New Chat", fg= "blue", command=self._openChat, font=("Courier New", "12")).grid(row=1, pady=10)
        # grid frame
        F2.grid(row=2, column=1, padx=20)

        # create menu for changing nickname and making new account
        menu = tk.Menu(self)
        settings = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Settings", menu=settings)
        settings.add_command(label="Edit Nickname", command=self._changeNickname)
        settings.add_command(label="Register New Account", command=self._createUser)
        self.config(menu=menu)



    def _openChat(self, event, LB: tk.Listbox, D: dict[str,int]) -> None:
        '''opens a new chatGUI when user clicks on a LB item'''

        # get the username the user selected
        user2: str = LB.get(LB.curselection())
        # clear user selection
        LB.selection_clear(0, tk.END)
        # get the corresponding userID
        user2ID: int = D[user2]
        # get the channelID between user and user2
        channelID: int = self._client.receiveChannelID(user2ID)
        # open chatGUI
        chatGUI(self, channelID, self._username, user2)
        


    def _removeChat(self, LB: tk.Listbox) -> None:
        '''removes a conversation'''

        # define remove function for use when user submits their list of conversations they want to remove
        def remove():
            # get the list of indices the user selected
            selected: list[int] = removeLB.curselection()
            if len(selected) > 0: # if the list is not empty
                # get the list of corresponding usernames
                selectedChats: list[str] = [removeLB.get(index) for index in selected]
                # get the list of corresponding userIDs while also popping them out from self._usernamesDict
                removedChatIDs = [self._usernamesDict.pop(chat) for chat in selectedChats]
                # get the list of corresponding channelIDs
                removedChatChannels = [self._client.receiveChannelID(id) for id in removedChatIDs]
                # for every channelID...
                for channelID in removedChatChannels:
                    # remove it from the database
                    self._client.removeConversation(channelID)

                LB.delete(0, tk.END)
                LB.insert(tk.END, *self._usernamesDict)

                removeWin.destroy()

        # create window for removing conversation
        removeWin = tk.Toplevel(self)
        convoList = LB.get(0, tk.END)
        removeWin.title("Remove Chat")

        # create label to tell user what to do
        tk.Label(removeWin, text="Select Conversation(s) to Remove", font=("Courier New", "13", "bold")).grid(row=0, column=0, padx=10, pady=10)
        
        # create frame to grid listbox and scrollbar
        F = tk.Frame(removeWin, pady=10)
        F.grid(sticky="ns")

        # create listbox and scrollbar
        S = tk.Scrollbar(F)
        removeLB = tk.Listbox(F, height=10, width=20, yscrollcommand=S.set, selectmode="multiple")
        removeLB.insert(tk.END, *convoList)
        removeLB.configure(font=("Courier New", "15"))
        removeLB.grid(row=0, column=0)
        S.grid(row=0, column=1, sticky='ns')
        S.config(command=LB.yview)

        # create a button to sumbit user choices
        tk.Button(removeWin, text="Submit", font=("Courier New", "13"), command=remove).grid(padx=10, pady=10)



    def _createChat(self, LB: tk.Listbox) -> None:
        '''creates a new chat channel with another user'''

        # define enter function for when user clicks enter key
        def enter(event):
            # get the username
            username = entryText.get()
            # clear the entry widget
            usernameEntry.delete(0, tk.END)
            # get the userID that corresponds with the user given username
            userID = self._client.receiveUserID(username)
            if userID != None: # if the username exists...
                # create a new conversation
                self._client.addConversation(username)
                # insert the nickname into the LB
                LB.insert(tk.END, username)
                # destroy createWin
                createWin.destroy()
            else: # if the username does not exist...
                tkmb.showerror("Error", "Invalid username, please double check and try again")
                createWin.focus_set()

        # create a window for changing nickname
        createWin = tk.Toplevel(self)
        createWin.title("Open New Conversation")
        createWin.focus_set()

        # create StringVar for entry widget
        entryText = tk.StringVar()

        # create frame to grid label and entry widget
        F = tk.Frame(createWin)
        F.grid(row=1, pady=10)

        # populate createWin
        tk.Label(createWin, text="Type in a valid username", font=("Courier New", 10)).grid(row=0, padx=10, pady=10)
        tk.Label(F, text="Username:").grid(row=0, column=0, padx=3)
        usernameEntry = tk.Entry(F, textvariable=entryText)
        usernameEntry.bind("<Return>", enter)
        usernameEntry.grid(row=0, column=1)



    def _changeNickname(self) -> None:
        '''changes the user's nickname'''

        # define enter function for when user clicks enter key
        def enter(event):
            # get the nickname
            nickname = entryText.get()
            # clear the entry widget
            nicknameEntry.delete(0, tk.END)
            if nickname not in nickList: # if the nickname isn't a duplicate...
                # update user's nickname in database
                self._client.updateProfile(nickname)
                # update instance variable
                self._username = nickname
                # update self._nameLabel to match new username
                self._nameLabel.config(text=f"Welcome {self._username}")
                # destroy nickWin
                nickWin.destroy()
            else: # if the nickname is a duplicate
                tkmb.showerror("Error", "Duplicate nickname, please choose another nickname")
                nickWin.focus_set()

        # create a window for changing nickname
        nickWin = tk.Toplevel(self)
        nickWin.title("Change Nickname")
        nickWin.focus_set()
        
        # get the list of tuples of all userIDs and usernames
        users = self._client.receiveProfileUpdates()
        # get all the usernames
        nickList: list[str] = [user[1] for user in users]
        entryText = tk.StringVar()

        # create frame to grid label and entry widget
        F = tk.Frame(nickWin)
        F.grid(row=1, padx=10, pady=10)

        # populate nickWin
        tk.Label(nickWin, text="Type in a new username", font=("Courier New", 10)).grid(row=0, padx=10, pady=10)
        tk.Label(F, text="New Nickname:").grid(row=1, column=0)
        nicknameEntry = tk.Entry(nickWin, textvariable=entryText)
        nicknameEntry.bind("<Return>", enter)
        nicknameEntry.grid(row=1, column=1)



    def _createUser(self) -> None:
        '''creates a new user in the system'''

        def submit():
            username = usernameText.get()
            password = passwordText.get()
            usernameEntry.delete(0, tk.END)
            passwordEntry.delete(0, tk.END)
            if username not in nickList:
                self._client.register(username, password)
                tkmb.showinfo("Successful", "The new user was successfully created")
                newUserWin.destroy()
            else:
                tkmb.showerror("Error", "Duplicate username, please choose another username")
                newUserWin.focus_set()
            

        # create a window for creating a new user
        newUserWin = tk.Toplevel(self)
        newUserWin.title("Register New User")
        newUserWin.focus_set()
        # create a frame to grid labels and entry widgets
        F = tk.Frame(newUserWin)
        F.grid(row=1, padx=10)

        # get the list of tuples of all userIDs and usernames
        users = self._client.receiveProfileUpdates()
        # get all the usernames
        nickList: list[str] = [user[1] for user in users]
        # create StringVars for entry widgets
        usernameText = tk.StringVar()
        passwordText = tk.StringVar()

        # populate newUserWin
        tk.Label(newUserWin, text="Create an account", font=("Courier New", 10)).grid(row=0, pady=10)
        tk.Label(F, text="Username:").grid(row=0, column=0, pady=3)
        tk.Label(F, text="Password:").grid(row=1, column=0, pady=3)
        usernameEntry = tk.Entry(F, textvariable=usernameText)
        usernameEntry.grid(row=0, column=1)
        passwordEntry = tk.Entry(F, textvariable=passwordText)
        passwordEntry.grid(row=1, column=1)
        tk.Button(newUserWin, text="Submit", command=submit).grid(row=2, pady=10)



class chatGUI(tk.Toplevel):
    
    DELAY_TIME = 1000
    def __init__(self, master: tk.Toplevel, connection: client.Client, channel: int, user1: str, user1ID: int, user2: str, user2ID: int) -> None:
        super().__init__(master)
        self.title("Chat")
        self._channelID = channel
        self._client = connection
        self._mainUser = user1
        self._mainUserID = user1ID
        self._user2 = user2
        self._user2ID = user2ID
        self._message = tk.StringVar()
        self._lastPollTime = time.time()

        tk.Label(self, text=self._user2, font=("Helvetica", "20")).grid(padx=20, pady=10, sticky="w")

        lastLogin = self._client.getLastLogin(self._user2ID)
        if lastLogin == 0:
            self._lastLoginLabel = tk.Label(self, text="Online", fg="green")
        else:
            curr = time.time()
            difference = curr - lastLogin
            self._lastLoginLabel = tk.Label(self, text=str(divmod(difference, 3600)[0]))
        self._lastLoginLabel.grid(sticky="w", padx=20)

        texts = self._client.openConversation(self._channelID)
        self._textBox = st.ScrolledText(self, height=20, width=30)
        for text in texts:
            if text[0] == self._mainUserID:
                self._textBox.insert(tk.END, "\n"+"You: "+text[1])
            else:
                self._textBox.insert(tk.END, "\n"+self._user2+": "+text[1])
        self._textBox.config(state='disabled')
        self._textBox.grid(padx=10, pady=10)
        self._textBox.yview_moveto(1)
        
        self._messageEntry = tk.Entry(self, textvariable=self._message)
        self._messageEntry.bind("<Return>", self.sendMessage)
        self._messageEntry.grid(padx=10, pady=10)

        self.after(chatGUI.DELAY_TIME, self.receiveMessage)



    def sendMessage(self, event) -> None:
        message = self._message.get()
        self._messageEntry.delete(0, tk.END)
        self._textBox.config(state="normal")
        self._textBox.insert(tk.END, "\n"+"You: "+message)
        self._textBox.config(state="disabled")
        self._textBox.yview_moveto(1)

        self._client.sendMessage(message, self._channelID)



    def receiveMessage(self) -> None:
        messages: list[tuple[int, str]] = self._client.receiveMessages(self._channelID, self._lastPollTime)
        self._textBox.config(state="normal")
        for message in messages:
            if message[0] == self._mainUserID:
                self._textBox.insert(tk.END, "\n"+"You: "+message[1])
            else:
                self._textBox.insert(tk.END, "\n"+self._user2+": "+message[1])
        self._textBox.config(state="disabled")

        self._lastPollTime = time.time()

        self.after(chatGUI.DELAY_TIME, self.receiveMessage)



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
        self._userID = self._client.login(self._usernameVar.get(), self._passwordVar.get())

        if self._userID == None:
            tkmb.showerror("Error", "Login failed. Please check your username and password and try again")
        else:
            main = MainGUI(self, self._client, self._userID, self._usernameVar.get())

            self._usernameEntry.delete(0, tk.END)
            self._passwordEntry.delete(0, tk.END)

            self.destroy()
            self.wait_window(main)
            self.quit()



loginGUI().mainloop()