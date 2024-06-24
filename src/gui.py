import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.scrolledtext as st
import client
import time

class MainGUI(tk.Toplevel):
    DELAY_TIME = 10000

    def __init__(self, master: tk.Tk, connection: client.Client, userID: int, username: str):
        '''creates the main chat app window'''

        # create instance variables
        super().__init__(master)
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
        LB = tk.Listbox(F1, height=10, width=20, yscrollcommand=S.set)
        # get the list of users that the client has conversed with
        self._usernamesList: list[tuple[str, int]] = self._client.receiveUsernames()[0]
        # get whether or not the channels are visible to the client
        self._visibility = self._client.getVisibility()[0]
        if len(self._usernamesList) != 0:
            for i in range(len(self._usernamesList)):
                if self._visibility[i]: # if the visibility is True, show the user
                    username = self._usernamesList[i][0]
                    LB.insert(tk.END, username)
        LB.configure(font=("Courier New", "15"))
        LB.bind("<<ListboxSelect>>", lambda event: self._openChat(event, LB, self._usernamesList))
        LB.grid(row=0, column=0)
        # config scrollbar together with listbox
        S.config(command=LB.yview)
        # grid frame
        F1.grid(row=2, column=0, padx=10, pady=10)

        # create frame to grid two buttons
        F2 = tk.Frame(self)

        # create button to delete chat and open a new chat
        tk.Button(F2, text="Delete Chat", fg="red", command=lambda: self._removeChat(LB), font=("Courier New", "12")).grid(row=0, pady=10)
        tk.Button(F2, text="New Chat", fg= "blue", command=lambda: self._createChat(LB), font=("Courier New", "12")).grid(row=1, pady=10)
        # grid frame
        F2.grid(row=2, column=1, padx=20)

        # create menu for changing nickname and making new account
        menu = tk.Menu(self)
        settings = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Settings", menu=settings)
        settings.add_command(label="Edit Nickname", command=self._changeNickname)
        settings.add_command(label="Register New Account", command=self._createUser)
        self.config(menu=menu)

        # update the list of conversations after every DELAY_TIME
        self.after(MainGUI.DELAY_TIME, lambda: self._getNewConvos(LB))


 
    def _openChat(self, event, LB: tk.Listbox, D: list[tuple[str, int]]) -> None:
        '''opens a new chatGUI when user clicks on a LB item'''

        # get the username the user selected
        user2: int = LB.curselection()[0]
        user2Name = LB.get(user2)
        # clear user selection
        LB.selection_clear(0, tk.END)
        # get the corresponding userID
        user2ID: int = D[user2][1]
        # get the channelID between user and user2
        channelID: int = self._client.receiveChannelID(user2ID)[0]
        # open chatGUI
        chatGUI(self, self._client, channelID, self._userID, user2Name, user2ID)
        


    def _removeChat(self, LB: tk.Listbox) -> None:
        '''removes a conversation'''

        # define remove function for use when user submits their list of conversations they want to remove
        def remove():
            # get the list of indices the user selected
            selected: list[int] = removeLB.curselection()
            if len(selected) > 0: # if the list is not empty
                # get the list of corresponding usernames
                selectedChats: list[str] = [removeLB.get(index) for index in selected]
                # get the list of corresponding userIDs while also popping them out from self._usernamesList
                removedChatIDs = [self._usernamesList[index] for index in selected]
                for id in removedChatIDs:
                    self._usernamesList.remove(id)
                # get the list of corresponding channelIDs
                removedChatChannels = [self._client.receiveChannelID(id[1]) for id in removedChatIDs]
                # for every channelID...
                for channelID in removedChatChannels:
                    # remove it from the database
                    self._client.removeConversation(channelID[0])

                # get the new list of users and update LB
                users = [item[0] for item in self._usernamesList]
                LB.delete(0, tk.END)
                LB.insert(tk.END, *users)

                LB.bind("<<ListboxSelect>>", lambda event: self._openChat(event, LB, self._usernamesList))
                removeWin.destroy()

        # define reBind function to rebind function to <<ListboxSelect>>
        def reBind():
            LB.bind("<<ListboxSelect>>", lambda event: self._openChat(event, LB, self._usernamesList))
            removeWin.destroy()


        # unbind _openChat from LB to prevent IndexErrors
        LB.unbind("<<ListboxSelect>>")

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

        # on window close, call reBind
        removeWin.protocol("WM_DELETE_WINDOW", reBind)



    def _createChat(self, LB: tk.Listbox) -> None:
        '''creates a new chat channel with another user'''

        # define enter function for when user clicks enter key
        def enter(event):
            # get the username
            username = entryText.get()
            # clear the entry widget
            usernameEntry.delete(0, tk.END)
            # get the userID that corresponds with the user given username
            userID = self._client.receiveUserID(username)[0]

            # if the channel already exists and is visible to the user
            if (username, userID) in self._usernamesList and self._visibility[self._usernamesList.index((username, userID))]:
                tkmb.showinfo("Notice", "Channel already exists")
                createWin.destroy()
            else: 
                if userID != None: # if the username exists...
                    # create a new conversation
                    self._client.addConversation(username)
                    # insert the nickname into the LB and self._usernamesList
                    LB.insert(tk.END, username)
                    self._usernamesList.append((username, userID))
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
        tk.Label(F, text="New Nickname:").grid(row=0, column=0)
        nicknameEntry = tk.Entry(F, textvariable=entryText)
        nicknameEntry.bind("<Return>", enter)
        nicknameEntry.grid(row=0, column=1)



    def _createUser(self) -> None:
        '''creates a new user in the system'''
        registrationWin = RegistrationGUI(self, self._client)
        self.wait_window(registrationWin)

    

    def _getNewConvos(self, LB: tk.Listbox) -> None:
        '''poll for changes in conversation list'''

        # clear LB
        LB.delete(0, tk.END)
        # get the list of users the client has conversed with
        self._usernamesList = self._client.receiveUsernames()[0]
        # get the correspondinb visiblity of the respecive channels
        self._visibility = self._client.getVisibility()[0]
        if len(self._usernamesList) != 0:
            for i in range(len(self._usernamesList)):
                if self._visibility[i]: # if the visibility is True, display the user
                    username = self._usernamesList[i][0]
                    LB.insert(tk.END, username)

        # polls itself after DELAY_TIME
        self.after(MainGUI.DELAY_TIME, lambda: self._getNewConvos(LB))



class chatGUI(tk.Toplevel):
    DELAY_TIME = 1000

    def __init__(self, master: tk.Toplevel, connection: client.Client, channel: int, user1ID: int, user2: str, user2ID: int) -> None:
        '''creates a chatGUI window for conversation'''

        # create instance variables
        super().__init__(master)
        self.title("Chat")
        self._channelID = channel
        self._client = connection
        self._mainUserID = user1ID
        self._user2 = user2
        self._user2ID = user2ID
        self._message = tk.StringVar()
        self._lastPollTime = time.time()

        # display the username of the user the client is conversing with
        tk.Label(self, text=self._user2, font=("Helvetica", "20")).grid(padx=20, pady=10, sticky="w")

        # get the last login time of the other user
        lastLogin = self._client.getLastLogin(self._user2ID)[0]
        if lastLogin == 0: # if the other user is currently online
            self._lastLoginLabel = tk.Label(self, text="Online", fg="green")
        else: # if the other user is currently offline
            # get the time difference from when the other user logged off until now
            curr = time.time()
            difference = curr - lastLogin
            # display the difference
            if divmod(difference, 3600)[0] == 0:
                self._lastLoginLabel = tk.Label(self, text=f"Last online {int(divmod(difference, 60)[0])} minutes ago")
            else:
                self._lastLoginLabel = tk.Label(self, text=f"Last online {int(divmod(difference, 3600)[0])} hours ago")
        self._lastLoginLabel.grid(sticky="w", padx=20)

        # get messages
        texts = self._client.openConversation(self._channelID)[0]
        self._textBox = st.ScrolledText(self, height=20, width=40)
        if len(texts) != 0:
            for text in texts:
                if text[0] == self._mainUserID:
                    self._textBox.insert(tk.END, "\n"+"You: "+text[1])
                else:
                    self._textBox.insert(tk.END, "\n"+self._user2+": "+text[1])
        # disable editing the text widget
        self._textBox.config(state='disabled')
        self._textBox.grid(padx=10, pady=10)
        # move the viewpoint to the bottom (the most current message)
        self._textBox.yview_moveto(1)
        
        # create an entry widget for the user to send messages
        self._messageEntry = tk.Entry(self, textvariable=self._message, width=40)
        self._messageEntry.bind("<Return>", self.sendMessage)
        self._messageEntry.grid(padx=10, pady=10)

        # poll for new messages after DELAY_TIME
        self.after(chatGUI.DELAY_TIME, self.receiveMessage)



    def sendMessage(self, event) -> None:
        '''send message to the other user'''

        # get the message
        message = self._message.get()
        # clear the entry widget
        self._messageEntry.delete(0, tk.END)
        if len(message) != 0:
            # enable editing for text widget
            self._textBox.config(state="normal")
            # display the message at the bottom of the text widget
            self._textBox.insert(tk.END, "\n"+"You: "+message)
            # disable editing of text widget
            self._textBox.config(state="disabled")
            self._textBox.yview_moveto(1)

            # send the message to the other client
            self._client.sendMessage(message, self._channelID)



    def receiveMessage(self) -> None:
        '''receive messages and online status of the other user'''

        # receive messages
        messages: list[tuple[int, str]] = self._client.receiveMessages(self._channelID, self._lastPollTime)[0]
        
        if len(messages) != 0: # if messages were received
            # enable editing of text widget
            self._textBox.config(state="normal")
            for message in messages:
                if message[0] != self._mainUserID: # if the other user sent the message, display the message
                    self._textBox.insert(tk.END, "\n"+self._user2+": "+message[1])
            # disable editing of text widget
            self._textBox.config(state="disabled")

        # set _lastPollTime to the current time
        self._lastPollTime = time.time()

        # get the last login time of the other user
        lastLogin = self._client.getLastLogin(self._user2ID)[0]
        if lastLogin == 0: # if the other user is currently online
            self._lastLoginLabel.config(text="Online", fg="green")
        else: # if the other user is currently offline
            # get the time difference from when the other user logged off until now
            cur = time.time()
            difference = cur - lastLogin
            # display the difference
            if divmod(difference, 3600)[0] == 0:
                self._lastLoginLabel.config(text=f"Last online {int(divmod(difference, 60)[0])} minutes ago", fg="black")
            else:
                self._lastLoginLabel.config(text=f"Last online {int(divmod(difference, 3600)[0])} hours ago", fg="black")

        # polls itself after DELAY_TIME
        self.after(chatGUI.DELAY_TIME, self.receiveMessage)



class loginGUI(tk.Tk):
    def __init__(self) -> None:
        '''creates a window for the user to enter their username and password
           shows an error MessageBox if username and/or password does not match database records
           creates the main gui window if records match'''

        # create instance variables
        super().__init__()
        self.title("Login")
        self._usernameVar = tk.StringVar()
        self._passwordVar = tk.StringVar()
        self._client = client.Client()
        
        # populate the window
        tk.Label(self, text="Sign In", font=("Helvetica", "20")).grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(self, text="Username", font=("Helvetica", "12")).grid(row=1, column=0, padx=10)
        tk.Label(self, text="Password", font=("Helvetica", "12")).grid(row=2, column=0, padx=10)

        self._usernameEntry = tk.Entry(self, textvariable=self._usernameVar)
        self._passwordEntry = tk.Entry(self, textvariable=self._passwordVar)
        self._usernameEntry.grid(row=1, column=1, padx=10, pady=10)
        self._passwordEntry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self, text="Login", font=("Helvetica", "12"), command=self.checkCredential).grid(row=3, column=0, padx=10, pady=10, columnspan=2)
        tk.Button(self, text="Register", font=("Helvetica", "12"), command=self.openRegistrationWindow).grid(row=4, padx=10, pady=10, columnspan=2)



    def openRegistrationWindow(self) -> None:
        '''open a RegistrationGUI to register a new user'''

        registerWin = RegistrationGUI(self, self._client)
        self.wait_window(registerWin)



    def checkCredential(self) -> None:
        '''check if the username and password matches data base records'''

        # try to get the userID that matches with the given username and password
        self._userID = self._client.login(self._usernameVar.get(), self._passwordVar.get())

        if self._userID == None: # if records didn't match
            tkmb.showerror("Error", "Login failed. Please check your username and password and try again")
            self._usernameEntry.delete(0, tk.END)
            self._passwordEntry.delete(0, tk.END)
        else: # if records match
            main = MainGUI(self, self._client, self._userID, self._usernameVar.get())

            self._usernameEntry.delete(0, tk.END)
            self._passwordEntry.delete(0, tk.END)

            # make loginGUI invisible
            self.withdraw()
            self.wait_window(main)
            self.quit()



class RegistrationGUI(tk.Toplevel):
    def __init__(self, master: tk.Tk, client: client.Client) -> None:
        super().__init__(master)
        self._master = master
        self._client = client
        
        # create a window for creating a new user
        self.title("Register New User")
        self.focus_set()
        # create a frame to grid labels and entry widgets
        F = tk.Frame(self)
        F.grid(row=1, padx=10)

        # create StringVars for entry widgets
        self._usernameText = tk.StringVar()
        self._passwordText = tk.StringVar()

        # populate window
        tk.Label(self, text="Create an account", font=("Courier New", 10)).grid(row=0, pady=10)
        tk.Label(F, text="Username:").grid(row=0, column=0, pady=3)
        tk.Label(F, text="Password:").grid(row=1, column=0, pady=3)

        self._usernameEntry = tk.Entry(F, textvariable=self._usernameText)
        self._usernameEntry.grid(row=0, column=1)

        self._passwordEntry = tk.Entry(F, textvariable=self._passwordText)
        self._passwordEntry.grid(row=1, column=1)

        tk.Button(self, text="Submit", command=self.submit).grid(row=2, pady=10)



    def submit(self):
        '''Submit registration info'''

        # get username and password
        username = self._usernameText.get()
        password = self._passwordText.get()

        # clear entry widgets
        self._usernameEntry.delete(0, tk.END)
        self._passwordEntry.delete(0, tk.END)

        # register the user and get the status
        success = self._client.register(username, password)
        if success: # if the registration was successful
            tkmb.showinfo("Successful", "The new user was successfully created")
            self.destroy()
        else: # if the username is a duplicate
            tkmb.showerror("Error", "Duplicate username, please choose another username")
            self.focus_set()


loginGUI().mainloop()