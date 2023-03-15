import customtkinter
from customtkinter import *
import tkinter.messagebox
from tkinter import *
from PIL import *
import socket
import threading
import glob
import pyglet
import time
import os

from labelDesign import TextDesign

class GUI:
    
    # Get CurrentWorkingDirectory Path
    folderLocation = os.getcwd()

    # Basic values
    SCREEN_WIDTH = 1270
    SCREEN_HEIGHT = 720
    FONT_FOLDER = folderLocation + r'\Fonts'
    IMAGE_FOLDER = folderLocation + r'\CTk_Images'
    RED_FG = "#7d070f"
    LIGHT_RED_FG = "#ff5c67"
    GREEN_FG = "#077d0f"
    BLUE_FG = "#12bdc9"
    MAX_CLIENTS = 50
    clients = []

    # Set basic emojis for server up / down
    redCircle = CTkImage(light_image=Image.open(IMAGE_FOLDER+r"\redCircle.png"))
    greenCircle = CTkImage(light_image=Image.open(IMAGE_FOLDER+r"\greenCircle.png"))
    brain = CTkImage(light_image=Image.open(IMAGE_FOLDER+r"\brain.png"))

    # Set fonts for Tkinter.Canvas (cannot use external fonts like customtkinter)
    fonts = glob.glob(f"{FONT_FOLDER}" + r"\random\*.ttf")
    for font in fonts:
        pyglet.font.add_file(font)
    # ------------------------- INITIATE CLASS -------------------------

    def __init__(self):
        """
        * Creates server and screen.
        """
        # Set screen appearance + start server
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")

        dnsClient = socket.socket()
        dnsClient.connect(('192.168.1.153', 11111))
        dnsClient.send(f'set {socket.gethostbyname(socket.gethostname())}'.encode())
        self.code = dnsClient.recv(1024).decode()
        dnsClient.close()

        self.server = socket.socket()
        self.server.bind(('0.0.0.0', 25565))
        self.server.listen(self.MAX_CLIENTS)
        threading.Thread(target=self.startServer).start()

        self.screen = CTk()

        self.screen.title("Brainstorm by Yuval Goldberger")
        self.screen.geometry(f'{self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}')

        self.createDefaultScreen()

    def createDefaultScreen(self):
        """
        * Creates the default (settings) screen.
        """

        self.SERVER_STARTED = False
        self.SHOW_NAMES = False
        self.SUBJECT = ''
        self.associations = []

        # Main label (Welcome to brainstorm)
        mainLabel = CTkLabel(self.screen, text="!סיעור מוחות", font=("Assistant ExtraBold", 60))
        mainLabel.pack()

        # Code label
        codeLabel = CTkLabel(self.screen, text=f'התחברו עם הקוד: {self.code}', font=("Assistant SemiBold", 30))
        codeLabel.pack()

        # Scrollbar to choose amount of partifipants
        optionsLabel = CTkLabel(self.screen, text="בחר כמות משתתפים", font=("Assistant SemiBold", 25))
        optionsLabel.place(relx = 0.25, rely = 0.25, anchor=E)

        options = [f'{self.MAX_CLIENTS} Participants (Default)'] + [f'{i-1} Participants' for i in range(self.MAX_CLIENTS, self.MAX_CLIENTS - 30, -1)]
        self.optionsParticipants = CTkOptionMenu(self.screen, values=options, text_color="#000000", fg_color="#c3ecf7", command=self.getParticipantsAmount)
        self.optionsParticipants.place(relx = 0.2, rely=0.3, anchor=E)

        # Entry and label for subject
        addSubject = CTkLabel(self.screen, text="הכנס נושא בתיבת הטקסט", font=("Assistant Bold", 35))
        addSubject.place(relx=0.5, rely=0.3, anchor=CENTER)
        self.subjectEntry = CTkEntry(self.screen, placeholder_text="..הכנס נושא", font=("Assistant Medium", 15), justify='right', width=550, height=100)
        self.subjectEntry.place(relx=0.5, rely = 0.43, anchor=CENTER)

        # Button to show server's state
        self.serverUpButton = CTkButton(self.screen, image=self.redCircle, font=("Assistant Medium", 15), text=".הסיעור לא פעיל", hover=False, fg_color=self.RED_FG)
        self.serverUpButton.place(relx=0.01, rely = 0.98, anchor=SW)

        # Button to start brainstorm (send subject and start server)

        sendSubjectButton = CTkButton(self.screen, text="התחל סיעור מוחות", image=self.brain, font=("Assistant Medium", 15), command= self.subjButtonSend)
        sendSubjectButton.place(relx = 0.5, rely = 0.55, anchor=CENTER)

        # Mainloop
        self.screen.mainloop()

    # ------------------------- SERVER RELATED -------------------------

    def subjButtonSend(self):
        """
        * Starts the server thread.
        """
        if self.SERVER_STARTED == False:
            self.SUBJECT = self.subjectEntry.get()
            if len(self.SUBJECT) == 0 or self.SUBJECT == " " * len(self.SUBJECT):
                tkinter.messagebox.showerror("שגיאה", "לא הכנסת נושא")
            elif len(self.SUBJECT) <= 20:
                for client in self.clients:
                    try:
                        client[0].send(f'{self.SUBJECT}\n'.encode()) 
                    except:
                        self.clients.pop()
                self.changeWindow()
                self.SERVER_STARTED = True
            else:
                tkinter.messagebox.showerror("שגיאה", "הנושא צריך להיות פחות מ-20 תווים") 
        else:
            pass
    

    def startServer(self):
        """
        * Handles multi-client connections and sends them the subject when they connect 
        """
        # Starting amount of participants
        check = 0
        while True:
            try:
                newClient, newAddress = self.server.accept()
                self.clients.append((newClient, newAddress))
                print(newAddress, "connected")
                
                if check < self.MAX_CLIENTS:
                    threading.Thread(target=self.clientHandler, args=(newClient, newAddress), daemon=True).start()
                    print("will wait to a new client.")
            except:
                pass
    
    def clientHandler(self, client, address):
        """
        * Handles multi-client messages and appends it the the associations list  
        """
        while True:
            try:
                data = client.recv(1024).decode() # name:breakHere:message
                name = data.split(":breakHere:")[0]
                msg = data.split(":breakHere:")[1]
                print(f"{name} sent {msg}")


                print("adding")
                self.associations.append((name, msg))
                print(f"added {name}, {msg} to associations. it is now {self.associations}")
                self.updateAssociations()
            except:
                pass

    # ------------------------- GUI RELATED -------------------------
    
    def changeWindow(self):
        """
        * Destroys the first settings window and creates the Brainstorm window  
        """

        # Set values for images needed for buttons
        stop = CTkImage(light_image = Image.open(self.IMAGE_FOLDER+r"\stop.png"))
        beginner = CTkImage(light_image = Image.open(self.IMAGE_FOLDER+r"\beginner.png"))

        # Reset last window
        for widget in self.screen.winfo_children():
            widget.destroy()
<<<<<<< HEAD
=======
        
        time.sleep(0.5)
>>>>>>> parent of dc9bb7e (DNS Fix)

        # Create new window for new server
        subjectLabel = CTkLabel(self.screen, text=self.SUBJECT, font=("Assistant ExtraBold", 65))
        subjectLabel.pack()

        # Starts the Timer thread (so sleep() doesn't interfere with the entire code)
        self.countdown = True
        threading.Thread(target=self.timerInterval).start()

        # Associations Canvas
        self.canvas = Canvas(self.screen, width=1270, height=720, bg='#2c2c2c')
        self.canvas.pack()

        # Server status 
        self.serverUpButton = CTkButton(self.screen, image=self.greenCircle, font=("Assistant Medium", 15), text=".הסיעור פעיל", hover=False, fg_color=self.GREEN_FG)
        self.serverUpButton.place(relx=0.01, rely = 0.98, anchor=SW)

        # NameStateChange Button 
        namesStateButton = CTkButton(self.screen, image=beginner, font=("Assistant Medium", 15), text="הצג / הסתר שמות", command=self.nameStateChange)
        namesStateButton.place(relx=0.98, rely = 0.98, anchor=SE)

        # Restart Associations Settings 
        restartButton = CTkButton(self.screen, image=stop, text="אפס את ההגדרות", font=("Assistant Medium", 15), fg_color=self.LIGHT_RED_FG, command=self.restartGUI)
        restartButton.place(relx=0.5, rely = 0.962, anchor=CENTER)

    def nameStateChange(self):
        """
        * NameStateButton command that changes the associations in the screen (shows the name / removes them) 
        """
        self.SHOW_NAMES = not self.SHOW_NAMES
        self.updateAssociations()

    def getParticipantsAmount(self, choice):
        """
        * Gets chosen participants amount and sets it to the server 
        """
        self.MAX_CLIENTS = choice.split(" ")[0]
        print(self.MAX_CLIENTS)
        self.optionsParticipants.set(choice)
        
    def updateAssociations(self): 
        """
        * Resets associations and updates it to the newest form (happens when nameState changes or a new Association has been recieved) 
        """
        self.canvas.delete("all")
        time.sleep(0.5)
        # Show the associations 
        for a in self.associations:
            name = a[0]
            message = a[1]
            textDesign = TextDesign()
            fontName = textDesign.font.split(":")[0]
            fontStyle = textDesign.font.split(":")[1]
            association = self.canvas.create_text((textDesign.x, textDesign.y) , font=(fontName, textDesign.fontSize, fontStyle), fill=textDesign.color) 
            if self.SHOW_NAMES:      
                self.canvas.itemconfig(association, text=f'{name}\n{message}', angle=textDesign.angle)
            else:
                self.canvas.itemconfig(association, text=message, angle=textDesign.angle)
               
            self.canvas.pack()
            self.screen.update()

    def timerInterval(self):
        """
        * Sets a timer (30sec) for clients to send associations. If they don't they get disconnected.
<<<<<<< HEAD
        """
        import queue
        temp = CTkLabel(self.screen, font=(
                "Assistant Medium", 15))
        temp.place(relx=0.05, rely=0.05, anchor=NW)
        self.done = False
        q = queue.Queue()

        def changeText(i):
            try:
                if not temp.winfo_exists():
                    return
                if i == 0 or not self.countdown:
                    temp.destroy()
                    self.done = True
                    q.put(None)
                    return
                temp.configure(text=f'הזמן שנותר: {i} שניות')
                self.screen.update()
                threading.Timer(1, changeText, args=[i-1]).start()
            except:
                pass
        changeText(30)
        q.get()
        for i in self.clients:
            # Try-Except block as clients might have disconnected before
            client = i[0]
            try:
                client.send("disconnect from this brainstorm now\n".encode())
            except:
                self.clients.pop(self.clients.index(i))
                client.close()
        
=======
        """  
        for i in range(30, 0, -1):
            temp = CTkLabel(self.screen, text=f'הזמן שנותר: {i} שניות', font=("Assistant Medium", 15))
            temp.place(relx=0.05, rely = 0.05, anchor=NW)
            time.sleep(1)
            temp.destroy()
            if not self.countdown:
                break
        for i in range(len(self.clients)):
            # Try-Except block as clients might have disconnected before
            client = self.clients[i][0]
            try:
                client.send("disconnect\n".encode())
            except:
                self.clients.pop(i)
                client.close()
    
>>>>>>> parent of dc9bb7e (DNS Fix)
    def restartGUI(self):
        """
        * Resets the GUI (returns to settings window)
        """
        self.countdown = False
        # Reset last window
        for widget in self.screen.winfo_children():           
            widget.destroy()
            time.sleep(0.05)
        for i in self.clients:
            # Try-Except block as clients might have disconnected before
            client = i[0]
            try:
                client.send("disconnect from this brainstorm now\n".encode())
            except:
                self.clients.pop(self.clients.index(i))
                client.close()
                print("removed offline client")
        self.createDefaultScreen()
        

if __name__ == '__main__':
    GUI()