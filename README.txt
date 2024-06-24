CIS 41B Final Project

Created By:
    Tony Bai, James Nguyen

Description:
    A chat app made in python that uses sockets, multithreading,
    databases, and TK.

How to Run:
    1. Start the server by typing
        python src/server.py

    2. Open as many clients as needed by
        python src/gui.py

Files:
    src/client.py - James Nguyen
        Contains the client sided code of the GUI using sockets
    src/communication.py - James Nguyen
        Contains code to assist with the transfer of data between server
        and client using the sockets module
    src/database.py - Tony Bai
        Contains code to create, read, and modify the database as needed
        for the server. Uses the sqlite3 module
    src/gui.py - Tony Bai
        Contains the GUI Code that lets the user login, register,
        message others, etc. Uses the tk module.
    src/server.py - James Nguyen
        Contains the server sided code that processes multiple 
        user requests using threading. Uses both the socket 
        and threading module.

New Features:
    src/gui.py
        ...



