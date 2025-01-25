import kivy, kivymd, re, hashlib, random, ssl, smtplib, matplotlib, sqlite3, time, email, kivy_garden, datetime, cryptography
from kivy.uix.boxlayout import BoxLayout 
from kivy.lang import Builder 
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.spinner import Spinner
from kivymd.uix.list import OneLineListItem
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition, CardTransition, SwapTransition, FadeTransition, WipeTransition, FallOutTransition, RiseInTransition
from kivy.uix.floatlayout import FloatLayout
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from kivy.clock import Clock
from email.message import EmailMessage
from cryptography.fernet import Fernet

def HashPassword(Password):
    sha256 = hashlib.sha256()
    Passwd = bytes(Password.encode())
    sha256.update(Passwd)
    HashedPwd = sha256.hexdigest()
    return HashedPwd

def ValidEmail(Email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if(re.fullmatch(regex, Email)):
        return True
    return False 

def ValidUsername(User):
    conn = sqlite3.connect("Flashcard_App.db")
    c = conn.cursor()

    regex = bool(re.search(r"\s", User))
    if len(User) >= 1 and len(User) <= 30 and not regex:
        Usernames = c.execute("SELECT Username From UserAccount")
        Usernames = c.fetchall()
    
        for row in range(len(Usernames)):
            if User == Usernames[row][0]:
                conn.commit()
                conn.close()
                return False
        
        conn.commit()
        conn.close()
        return True
    else:
        conn.commit()
        conn.close()
        return False 
    

def ValidPassword(Password):
    regex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{12,30}$"
    if re.match(regex, Password) != None:
        return True
    else:
        return False

def Flip(Side):
    if Side == "Front":
        Side = "Back"
    else:
        Side = "Front"
    return Side

def searcherror(Screen, Text, dt):
    sm.get_screen(Screen).ids.searchbar.text = Text

class Demo1(Screen):
    def displayerror(dt):
        sm.get_screen('Login').ids.Error.text = ""
class Demo2(Screen):
    def displayerror(dt):
        sm.get_screen('SignUp').ids.Error.text = ""
class Demo3(Screen):
    def displayerror(dt):
        sm.get_screen('Account').ids.Error.text = ""

    def searcherror(dt):
        sm.get_screen("Account").ids.searchbar.text = ""
class Demo4(Screen):
    def displayerror(dt):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"SELECT Title FROM Flashcard WHERE SetID = '{Set}' ORDER BY FlashID DESC")
        Title = c.fetchone()[0]
        sm.get_screen('CreateNotes').ids.Title.text = Title

        conn.commit()
        conn.close()

    def searcherror(dt):
        sm.get_screen("CreateNotes").ids.searchbar.text = ""
class Demo5(Screen):
    def displayerror(dt):
        sm.get_screen('CreateSelection').ids.Error.text = ""

    def searcherror(dt):
        sm.get_screen("CreateSelection").ids.searchbar.text = ""
class Demo6(Screen):
    def searcherror(dt):
        sm.get_screen("Help").ids.searchbar.text = ""
class Demo7(Screen):
    def LatestActivity():
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"SELECT SetName FROM FlashcardSet WHERE UserID = '{UserID}' ORDER BY LastOpened DESC")
        RecentActivity = c.fetchall()
        if len(RecentActivity) == 0:
            sm.get_screen('Home').ids.Recent1.disabled = True
            sm.get_screen('Home').ids.Recent2.disabled = True
            sm.get_screen('Home').ids.Recent3.disabled = True
        elif len(RecentActivity) == 1:
            sm.get_screen('Home').ids.Recent1.text = RecentActivity[0][0]
            sm.get_screen('Home').ids.Recent1.disabled = False
            sm.get_screen('Home').ids.Recent2.disabled = True
            sm.get_screen('Home').ids.Recent3.disabled = True
        elif len(RecentActivity) == 2:
            sm.get_screen('Home').ids.Recent1.text = RecentActivity[0][0]
            sm.get_screen('Home').ids.Recent2.text = RecentActivity[1][0]
            sm.get_screen('Home').ids.Recent1.disabled = False
            sm.get_screen('Home').ids.Recent2.disabled = False
            sm.get_screen('Home').ids.Recent3.disabled = True
        else:
            sm.get_screen('Home').ids.Recent1.text = RecentActivity[0][0]
            sm.get_screen('Home').ids.Recent2.text = RecentActivity[1][0]
            sm.get_screen('Home').ids.Recent3.text = RecentActivity[2][0]
            sm.get_screen('Home').ids.Recent1.disabled = False
            sm.get_screen('Home').ids.Recent2.disabled = False
            sm.get_screen('Home').ids.Recent3.disabled = False

        conn.commit()
        conn.close()
    
    def searcherror(dt):
        sm.get_screen("Home").ids.searchbar.text = ""
class Demo8(Screen):
    def loadnotes(self, Screen, Condition):
        global Flashcards, Index, SideCard

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if sm.get_screen('LearnSelection').ids.spinner_id.text == "Flashcard Set":
            sm.get_screen('LearnSelection').ids.spinner_id.text = "You have not selected a set"
            Clock.schedule_once(Demo9.LoadError, 2)

            conn.commit()
            conn.close()
            return False
        Index = 0
        c.execute(f"SELECT SetID FROM FlashcardSet WHERE SetName = '{sm.get_screen('LearnSelection').ids.spinner_id.text}' \
                  and UserID = '{UserID}'")
        S_ID = c.fetchone()
        if Screen == "LearnNotes":
            c.execute(f"UPDATE Flashcard SET Viewed = 0 WHERE SetID = '{S_ID[0]}'")
            c.execute(f"UPDATE Flashcard SET Flagged = 0 WHERE SetID = '{S_ID[0]}'")
            c.execute(f"UPDATE Flashcard SET Learnt = 0 WHERE SetID = '{S_ID[0]}'")
            c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{S_ID[0]}'")
            Flashcards = c.fetchall()
        elif Screen == "Edit":
            c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{S_ID[0]}'")
            Flashcards = c.fetchall()
        elif Condition == "Learnt":
            Screen = "LearnNotes"
            c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{S_ID[0]}' AND Learnt = 1")
            Flashcards = c.fetchall()
        elif Condition == "Flagged":
            Screen = "LearnNotes"
            c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{S_ID[0]}' AND Flagged = 1")
            Flashcards = c.fetchall()
        elif Condition == "Easy":
            Screen = "LearnNotes"
            c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{S_ID[0]}' AND Difficulty = 'Easy'")
            Flashcards = c.fetchall()
        elif Condition == "Medium":
            Screen = "LearnNotes"
            c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{S_ID[0]}' AND Difficulty = 'Medium'")
            Flashcards = c.fetchall()
        elif Condition == "Hard":
            Screen = "LearnNotes"
            c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{S_ID[0]}' AND Difficulty = 'Hard'")
            Flashcards = c.fetchall()

        if len(Flashcards) == 0:
            sm.get_screen('LearnSelection').ids.spinner_id.text = "This set contains no flashcards"
            Clock.schedule_once(Demo9.LoadError, 2)
            conn.commit()
            conn.close()
            return False
        elif len(Flashcards) == 1: 
            sm.get_screen(Screen).ids.Next.disabled = True
            sm.get_screen(Screen).ids.Previous.disabled = True
        else:
            sm.get_screen(Screen).ids.Next.disabled = False
            sm.get_screen(Screen).ids.Previous.disabled = False

        
        c.execute(f"SELECT Format FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        Format = c.fetchone()[0]
        if Format == 1:
            sm.get_screen(Screen).ids.Flip.disabled = True
        else:
            sm.get_screen(Screen).ids.Flip.disabled = False
            
        c.execute(f"SELECT FrontCard FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        FrontCard = c.fetchone()[0]
        sm.get_screen(Screen).ids.Notes.text = FrontCard

        c.execute(f"SELECT Title FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        Title = c.fetchone()[0]
        sm.get_screen(Screen).ids.Title.text = Title

        if Screen == "LearnNotes":
            c.execute(f"SELECT Learnt FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
            Learnt = c.fetchone()[0]
            if Learnt == 1:
                sm.get_screen(Screen).ids.LearntButton.icon = "check"
            else:
                sm.get_screen(Screen).ids.LearntButton.icon = "close"

            c.execute(f"SELECT Flagged FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
            flag = c.fetchone()[0]
            if flag == 1:
                sm.get_screen(Screen).ids.FlagButton.icon = "check"
            else:
                sm.get_screen(Screen).ids.FlagButton.icon = "close"

            c.execute(f"UPDATE Flashcard SET Viewed = 1 WHERE FlashID = '{Flashcards[Index][0]}'")
            timestamp = int(time.time())
            c.execute(f"UPDATE FlashcardSet SET LastOpened = '{timestamp}' WHERE SetID = '{S_ID}'")

        SideCard = "Front"
        
        if Screen == "LearnNotes":
            sm.current = "LearnNotes"
        elif Screen == "Edit":
            sm.current = "Edit"

        conn.commit()
        conn.close()

    def searcherror(dt):
        sm.get_screen("LearnNotes").ids.searchbar.text = ""
    
class Demo9(Screen):
    def LoadError(dt):
        sm.get_screen("LearnSelection").ids.spinner_id.text = "Flashcard Set"

    def searcherror(dt):
        sm.get_screen("LearnSelection").ids.searchbar.text = ""
class Demo10(Screen):
    def LoadError(dt):
        sm.get_screen("Progress").ids.spinner_id.text = "Flashcard Set"

    def searcherror(dt):
        sm.get_screen("Progress").ids.searchbar.text = ""
class Demo11(Screen):
    pass
class Demo12(Screen):
    def searcherror(dt):
        sm.get_screen("Edit").ids.searchbar.text = ""

class InputAndButton(BoxLayout):
    def addset(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if self.ids.Title.text == "":
            sm.get_screen("CreateSelection").ids.Error.text = "No Title was entered"
            Clock.schedule_once(Demo5.displayerror, 2)
            conn.commit()
            conn.close()
            return False
        c.execute(f"SELECT SetName FROM FlashcardSet WHERE UserID = '{UserID}'")
        Titles = c.fetchall()
        for name in range(len(Titles)):
            if self.ids.Title.text == Titles[name][0]:
                sm.get_screen("CreateSelection").ids.Error.text = "This set already exists"
                Clock.schedule_once(Demo5.displayerror, 2)
                conn.commit()
                conn.close()
                return False
        c.execute(f"INSERT INTO FlashcardSet (SetName, NumCards, UserID) VALUES ('{self.ids.Title.text}', 0, {UserID})")
        self.ids.Title.text = ""
        
        conn.commit()
        conn.close()

class Graph(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(FigureCanvasKivyAgg(plt.gcf()))

    def Update(self):
        plt.clf()
        self.clear_widgets() 
        self.add_widget(FigureCanvasKivyAgg(plt.gcf()))

         

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.other_class = Demo8()

    def build(self):
        global sm
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"

        conn = sqlite3.connect("Flashcard_App.db")

        c = conn.cursor()

        c.execute("""CREATE TABLE if not exists UserAccount(
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT,
            Password TEXT,
            Email TEXT)
        """)

        c.execute("""CREATE TABLE if not exists Flashcard(
            FlashID INTEGER PRIMARY KEY AUTOINCREMENT,
            SetID INTEGER,
            Title TEXT,
            FrontCard TEXT,
            BackCard TEXT,
            Format BOOLEAN,
            Learnt BOOLEAN,
            Flagged BOOLEAN,
            Viewed BOOLEAN,
            Difficulty TEXT)
        """)

        c.execute("""CREATE TABLE if not exists FlashcardSet(
            SetID INTEGER PRIMARY KEY AUTOINCREMENT,
            SetName TEXT,
            NumCards INTEGER,
            UserID INTEGER,
            LastOpened INTEGER)
        """)

        c.execute("""CREATE TABLE if not exists MainProgress(
            ProgressID INTEGER PRIMARY KEY AUTOINCREMENT,
            SetID INTEGER)
        """)

        c.execute("""CREATE TABLE if not exists ProgressViewed(
            ViewedID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProgressID INTEGER,
            ProgressV REAL,
            ViewedDate INTEGER)
        """)

        c.execute("""CREATE TABLE if not exists ProgressLearnt(
            LearntID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProgressID INTEGER,
            ProgressL REAL,
            LearntDate INTEGER)
        """)

        c.execute("""CREATE TABLE if not exists ProgressFlagged(
            FlaggedID INTEGER PRIMARY KEY AUTOINCREMENT,
            ProgressID INTEGER,
            ProgressF REAL,
            FlaggedDate INTEGER)
        """)

        conn.commit()
        conn.close()
        
        from kivy.resources import resource_find
        filename = "main.kv"
        filename = resource_find(filename)
        if filename in Builder.files:
            Builder.unload_file(filename)
        Builder.load_file("main.kv")

        sm = ScreenManager()
        sm.add_widget(Demo1(name = "Login"))
        sm.add_widget(Demo2(name = "SignUp"))
        sm.add_widget(Demo3(name = "Account"))
        sm.add_widget(Demo4(name = "CreateNotes"))
        sm.add_widget(Demo5(name = "CreateSelection"))
        sm.add_widget(Demo6(name = "Help"))
        sm.add_widget(Demo7(name = "Home"))
        sm.add_widget(Demo8(name = "LearnNotes"))
        sm.add_widget(Demo9(name = "LearnSelection"))
        sm.add_widget(Demo10(name = "Progress"))
        sm.add_widget(Demo11(name = "Graph"))
        sm.add_widget(Demo12(name= "Edit"))
        return sm

    def Select(self, Difficulty):
        if Difficulty == "Easy":
            self.root.get_screen("CreateSelection").ids.Easy.icon = "check"
            self.root.get_screen("CreateSelection").ids.Medium.icon = "close"
            self.root.get_screen("CreateSelection").ids.Hard.icon = "close"
        elif Difficulty == "Medium":
            self.root.get_screen("CreateSelection").ids.Easy.icon = "close"
            self.root.get_screen("CreateSelection").ids.Medium.icon = "check"
            self.root.get_screen("CreateSelection").ids.Hard.icon = "close"
        elif Difficulty == "Hard":
            self.root.get_screen("CreateSelection").ids.Easy.icon = "close"
            self.root.get_screen("CreateSelection").ids.Medium.icon = "close"
            self.root.get_screen("CreateSelection").ids.Hard.icon = "check"


    
    def ClearFlashcard(self):
        self.root.get_screen("CreateNotes").ids.Title.text = ""
        self.root.get_screen("CreateNotes").ids.Notes.text = ""
  
    def ClearAccount(self):
        self.root.get_screen("Account").ids.NewUsername.text = ""
        self.root.get_screen("Account").ids.NewPassword.text = ""
        self.root.get_screen("Account").ids.NewEmail.text = ""

    def ClearHelp(self):
        self.root.get_screen("Help").ids.helpbox.text = ""
    
    def CheckDetails(self, MyPopup):
        global Code

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()
        
        c.execute(f"SELECT UserID FROM UserAccount WHERE Email = '{MyPopup.ids.Email.text}' \
            AND Username = '{MyPopup.ids.User.text}'")
        User = c.fetchone()
        if User == None:
            MyPopup.ids.ErrorMessage.text = "Details enetered are incorrect"
            conn.commit()
            conn.close()
            return False
        else:
            MyPopup.ids.ErrorMessage.text = f"Code sent to {MyPopup.ids.Email.text}"
            MyPopup.ids.Code.disabled = False
            MyPopup.ids.CodeButton.disabled = False

            email_sender = "appflashcard46@gmail.com"
            email_password = "fxsh sgkh ywcp phko"
            email_receiver = f"{MyPopup.ids.Email.text}"

            n = 6
            Code = ''.join(["{}".format(random.randint(0,9)) for num in range(0,n)])

            subject = "Reset Password Code"
            body = f"The code to reset your password is {Code}"

            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())

        conn.commit()
        conn.close()
    def CheckCode(self, MyPopup):
        if str(Code) == MyPopup.ids.Code.text:
            MyPopup.ids.Pwd.disabled = False
            MyPopup.ids.Submit.disabled = False
            MyPopup.ids.ErrorMessage.text = "Code typed was correct"
        else:
            MyPopup.ids.ErrorMessage.text = "Code typed was incorrect"
            MyPopup.ids.Code.text = ""


    def ChangePassword(self, MyPopup):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if ValidPassword(MyPopup.ids.Pwd.text):
            c.execute(f"UPDATE UserAccount SET Password = '{HashPassword(MyPopup.ids.Pwd.text)}' WHERE Username = '{MyPopup.ids.User.text}'")
            MyPopup.ids.ErrorMessage.text = "Password Updated"
        else:
            MyPopup.ids.ErrorMessage.text = "Password typed is invalid"

        conn.commit()
        conn.close()
    
    def searchclear(self, Screen):
        self.root.get_screen(Screen).ids.searchbar.text = ""

    def search(self, Screen):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"SELECT NumCards FROM FlashcardSet WHERE UserID = '{UserID}' \
                  AND SetName = '{self.root.get_screen(Screen).ids.searchbar.text}'")
        NumCards = c.fetchone()
        if NumCards == None or NumCards[0] == 0:
            self.root.get_screen(Screen).ids.searchbar.text = "This set does not exist or does not contain any cards"
            if Screen == "Account":
                Clock.schedule_once(Demo3.searcherror,2)
                conn.commit()
                conn.close()
                return False
            elif Screen == "CreateNotes":
                Clock.schedule_once(Demo4.searcherror,2)
                conn.commit()
                conn.close()
                return False
            elif Screen == "CreateSelection":
                Clock.schedule_once(Demo5.searcherror,2)
                conn.commit()
                conn.close()
                return False
            elif Screen == "Help":
                Clock.schedule_once(Demo6.searcherror,2)
                conn.commit()
                conn.close()
                return False
            elif Screen == "Home":
                Clock.schedule_once(Demo7.searcherror,2)
                conn.commit()
                conn.close()
                return False
            elif Screen == "LearnNotes":
                Clock.schedule_once(Demo8.searcherror,2)
                conn.commit()
                conn.close()
                return False
            elif Screen == "LearnSelection":
                Clock.schedule_once(Demo9.searcherror,2)
                conn.commit()
                conn.close()
                return False
            elif Screen == "Progress":
                Clock.schedule_once(Demo10.searcherror,2)
                conn.commit()
                conn.close()
                return False
            elif Screen == "Edit":
                Clock.schedule_once(Demo12.searcherror,2)
                conn.commit()
                conn.close()
                return False
        
        self.root.get_screen("LearnSelection").ids.spinner_id.text = self.root.get_screen(Screen).ids.searchbar.text   
        Demo8.loadnotes(self,"LearnNotes","")
        sm.current = "LearnNotes"

        conn.commit()
        conn.close()

    def loadnotes(self, Screen, Condition):
        Demo8.loadnotes(self, Screen, Condition)

    def signup(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if ValidEmail(self.root.get_screen('SignUp').ids.Email_textfield.text):
            if ValidUsername(self.root.get_screen('SignUp').ids.user_textfield.text):
                if ValidPassword(self.root.get_screen('SignUp').ids.password_textfield.text):
                    if self.root.get_screen('SignUp').ids.password_textfield.text == self.root.get_screen('SignUp').ids.confirm_password.text:
                        Password = HashPassword(self.root.get_screen('SignUp').ids.password_textfield.text)
                        User = self.root.get_screen('SignUp').ids.user_textfield.text
                        Email = self.root.get_screen('SignUp').ids.Email_textfield.text
                        
                        c.execute(f"INSERT INTO UserAccount (Username, Password, Email) VALUES (?,?,?)", (User, Password, Email,))
                        sm.current = "Login"
                    else:
                        self.root.get_screen('SignUp').ids.Error.text = "Passwords do not match"
                        Clock.schedule_once(Demo2.displayerror, 2)
                else:
                    self.root.get_screen('SignUp').ids.Error.text = "Password does not meet the requirements"
                    Clock.schedule_once(Demo2.displayerror, 2)
            else:
                self.root.get_screen('SignUp').ids.Error.text = "Username is already taken or does not meet the requiremnts"
                Clock.schedule_once(Demo2.displayerror, 2)
        else:
            self.root.get_screen('SignUp').ids.Error.text = "Email is not valid"
            Clock.schedule_once(Demo2.displayerror, 2)   

        conn.commit()
        conn.close()    

    def login(self):
        global UserID

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"SELECT Password FROM UserAccount WHERE Username = '{self.root.get_screen('Login').ids.user_field.text}'")
        Password = c.fetchone()
        HashedPwd = HashPassword(self.root.get_screen('Login').ids.password_field.text)
        if Password != None:
            if HashedPwd == Password[0]:
                c.execute(f"SELECT UserID FROM UserAccount WHERE Username = '{self.root.get_screen('Login').ids.user_field.text}'")
                UserID = c.fetchone()[0]
                sm.current = "Home"
                Demo7.LatestActivity()

            else:
                self.root.get_screen('Login').ids.Error.text = "The password does not match the username you have entered"
                Clock.schedule_once(Demo1.displayerror, 2)
        else:
            self.root.get_screen('Login').ids.Error.text = "One or more of the fields are not filled in correctly"
            Clock.schedule_once(Demo1.displayerror, 2)
        
        conn.commit()
        conn.close()

    def show_password_login(self, checkbox, value):
        if value:
            self.root.get_screen('Login').ids.password_field.password = False
            self.root.get_screen('Login').ids.password_text.text = "Hide Password"
            self.root.get_screen('Login').ids.password_field.icon_right = "eye"
        
        else:
            self.root.get_screen('Login').ids.password_field.password = True
            self.root.get_screen('Login').ids.password_text.text = "Show Password"
            self.root.get_screen('Login').ids.password_field.icon_right = "eye-off"

    def show_password_signup(self, checkbox, value):
        if value:
            self.root.get_screen('SignUp').ids.password_textfield.password = False
            self.root.get_screen('SignUp').ids.checkbox.text = "Hide Password"
            self.root.get_screen('SignUp').ids.password_textfield.icon_right = "eye"
            self.root.get_screen('SignUp').ids.confirm_password.password = False
            self.root.get_screen('SignUp').ids.confirm_password.icon_right = "eye"
        
        else:
            self.root.get_screen('SignUp').ids.password_textfield.password = True
            self.root.get_screen('SignUp').ids.checkbox.text = "Show Password"
            self.root.get_screen('SignUp').ids.password_textfield.icon_right = "eye-off"
            self.root.get_screen('SignUp').ids.confirm_password.password = True
            self.root.get_screen('SignUp').ids.confirm_password.icon_right = "eye-off"
    
    def clear(self, Screen):
        if Screen == "Login":
            self.root.get_screen(Screen).ids.user_field.text = ""
            self.root.get_screen(Screen).ids.password_field.text = ""
        elif Screen == "SignUp":
            self.root.get_screen(Screen).ids.Email_textfield.text = ""
            self.root.get_screen(Screen).ids.user_textfield.text = ""
            self.root.get_screen(Screen).ids.password_textfield.text = ""
            self.root.get_screen(Screen).ids.confirm_password.text = ""
        elif Screen == "CreateNotes":
            self.root.get_screen(Screen).ids.Title.text = ""
            self.root.get_screen(Screen).ids.Notes.text = ""
    
    def showdetails(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"SELECT Email FROM UserAccount WHERE UserID = '{UserID}'")
        Email = c.fetchone()[0]
        self.root.get_screen("Account").ids.Email.text = f"Current Email: {Email}"

        c.execute(f"SELECT Username FROM UserAccount WHERE UserID = '{UserID}'")
        Username = c.fetchone()[0]
        self.root.get_screen("Account").ids.User.text = f"Current Username: {Username}"

        conn.commit()
        conn.close()
    
    def UpdateUsername(self):

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if ValidUsername(self.root.get_screen("Account").ids.NewUsername.text):
            c.execute(f"UPDATE UserAccount SET Username = '{self.root.get_screen("Account").ids.NewUsername.text}' \
                      WHERE UserID = '{UserID}'")
            self.root.get_screen("Account").ids.User.text = f"Current Username: {self.root.get_screen("Account").ids.NewUsername.text}"
            self.root.get_screen("Account").ids.NewUsername.text = ""
            self.root.get_screen("Account").ids.Error.text = "Username has been changed"
            Clock.schedule_once(Demo3.displayerror, 2)
        else:
            self.root.get_screen("Account").ids.Error.text = "\n The username you typed in was not valid. \n Usernames must be between 1 and 30 characters containing no spaces." 
            Clock.schedule_once(Demo3.displayerror, 2)

        conn.commit()
        conn.close()

    def UpdatePassword(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if ValidPassword(self.root.get_screen("Account").ids.NewPassword.text):
            c.execute(f"UPDATE UserAccount SET Password = '{HashPassword(self.root.get_screen("Account").ids.NewPassword.text)}' \
                      WHERE UserID = '{UserID}'")
            self.root.get_screen("Account").ids.NewPassword.text = ""
            self.root.get_screen("Account").ids.Error.text = "Password has been changed"
            Clock.schedule_once(Demo3.displayerror, 2)
        else:
            self.root.get_screen("Account").ids.Error.text = "\n \nThe password that was typed was not valid. \n Password must contain at least 1 capital letter, special character \n and number, being between 12 and 30 characters in length"
            Clock.schedule_once(Demo3.displayerror, 2)

        conn.commit()
        conn.close()    

    def UpdateEmail(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if ValidEmail(self.root.get_screen("Account").ids.NewEmail.text):
            c.execute(f"UPDATE UserAccount SET Email = '{self.root.get_screen("Account").ids.NewEmail.text}' \
                      WHERE UserID = '{UserID}'")
            self.root.get_screen("Account").ids.Email.text = f"Current Username: {self.root.get_screen("Account").ids.NewEmail.text}"
            self.root.get_screen("Account").ids.NewEmail.text = ""
            self.root.get_screen("Account").ids.Error.text = "Email has been changed"
            Clock.schedule_once(Demo3.displayerror, 2)
        else: 
            self.root.get_screen("Account").ids.Error.text = "\n The email that was typed in was not valid"
            Clock.schedule_once(Demo3.displayerror, 2)

        conn.commit()
        conn.close()

    def addtextinput(self):
        self.root.get_screen("CreateSelection").ids.Create.disabled = True
        self.root.get_screen("CreateSelection").ids.box.add_widget(InputAndButton())
    
    def addvalues(self, Screen):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        self.root.get_screen(Screen).ids.spinner_id.values = []
        c.execute(f"SELECT SetName FROM FlashcardSet WHERE UserID = '{UserID}'")
        Sets = c.fetchall()
        for row in range(len(Sets)):
            self.root.get_screen(Screen).ids.spinner_id.values.append(Sets[row][0])

        conn.commit()
        conn.close()
    
    def spinner_clicked(self, Screen, value):
        self.root.get_screen(Screen).ids.click_label.text = f'You selected set: {value}'
        self.root.get_screen(Screen).ids.spinner_id.text = value
    
    def Format(self, Format):
        global Set, Side, PrevScreen
        
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        PrevScreen = "CreateSelection"

        if self.root.get_screen('CreateSelection').ids.spinner_id.text == "Flashcard Set":
            self.root.get_screen('CreateSelection').ids.Error.text = "You have not selected a set"
            Clock.schedule_once(Demo5.displayerror, 2)
            conn.commit()
            conn.close()
            return False

        if self.root.get_screen('CreateSelection').ids.Easy.icon == "check":
            Difficulty = "Easy"
        elif self.root.get_screen('CreateSelection').ids.Medium.icon == "check":
            Difficulty = "Medium"
        elif self.root.get_screen('CreateSelection').ids.Hard.icon == "check":
            Difficulty = "Hard"
        else:
            self.root.get_screen('CreateSelection').ids.Error.text = "You have not selected a difficulty"
            Clock.schedule_once(Demo5.displayerror, 2)
            conn.commit()
            conn.close()
            return False
        
        c.execute(f"SELECT SetID FROM FlashcardSet WHERE SetName = '{self.root.get_screen('CreateSelection').ids.spinner_id.text}' \
            and UserID = '{UserID}'")
        Set = c.fetchone()[0]

        c.execute(f"INSERT INTO Flashcard (SetID, Format, Learnt, Flagged, Viewed, Difficulty) VALUES ({Set}, {Format}, 0, 0, 0, '{Difficulty}')")

        c.execute(f"INSERT INTO MainProgress (SetID) VALUES ({Set})")

        sm.current = "CreateNotes"
        if Format == 1:
            self.root.get_screen("CreateNotes").ids.FlipCard.disabled = True
        else:
            self.root.get_screen("CreateNotes").ids.FlipCard.disabled = False

        Side = "Front"

        conn.commit()
        conn.close()
        
    def FlipCardCreate(self):
        global Side

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if  PrevScreen == "Edit":
            Side = Flip(Side)

            if Side == "Back":
                    c.execute(f"UPDATE Flashcard SET FrontCard = '{self.root.get_screen('CreateNotes').ids.Notes.text}' \
                            WHERE FlashID = '{Flashcards[Index][0]}'")
                
                    c.execute(f"SELECT BackCard FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
                    BackCard = c.fetchone()[0]
                    if BackCard == None:
                        self.root.get_screen('CreateNotes').ids.Notes.text = ""
                    else:
                        self.root.get_screen('CreateNotes').ids.Notes.text = BackCard
                

            else:
                c.execute(f"UPDATE Flashcard SET BackCard = '{self.root.get_screen('CreateNotes').ids.Notes.text}' \
                        WHERE FlashID = '{Flashcards[Index][0]}'")
                
                c.execute(f"SELECT FrontCard FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
                FrontCard = c.fetchone()[0]
                if FrontCard == None:
                    self.root.get_screen('CreateNotes').ids.Notes.text = ""
                else:
                    self.root.get_screen('CreateNotes').ids.Notes.text = FrontCard
        
        else:
            c.execute(f"SELECT FlashID FROM Flashcard WHERE SetID = '{Set}'")
            Flash = c.fetchall()[-1][0]
            Side = Flip(Side)
            if Side == "Back":
                c.execute(f"UPDATE Flashcard SET FrontCard = '{self.root.get_screen('CreateNotes').ids.Notes.text}' \
                        WHERE FlashID = '{Flash}'")
            
                c.execute(f"SELECT BackCard FROM Flashcard WHERE FlashID = '{Flash}'")
                BackCard = c.fetchone()[0]
                if BackCard == None:
                    self.root.get_screen('CreateNotes').ids.Notes.text = ""
                else:
                    self.root.get_screen('CreateNotes').ids.Notes.text = BackCard
            

            else:
                c.execute(f"UPDATE Flashcard SET BackCard = '{self.root.get_screen('CreateNotes').ids.Notes.text}' \
                        WHERE FlashID = '{Flash}'")
                
                c.execute(f"SELECT FrontCard FROM Flashcard WHERE FlashID = '{Flash}'")
                FrontCard = c.fetchone()[0]
                if FrontCard == None:
                    self.root.get_screen('CreateNotes').ids.Notes.text = ""
                else:
                    self.root.get_screen('CreateNotes').ids.Notes.text = FrontCard

        conn.commit()
        conn.close()

    def back(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if PrevScreen == "CreateSelection":
            c.execute(f"SELECT FlashID FROM Flashcard WHERE SetID = '{Set}'")
            Flash = c.fetchall()[-1][0]
            c.execute(f"DELETE FROM Flashcard WHERE FlashID = '{Flash}'")
            sm.current = "CreateSelection"
        else:
            sm.current = "Edit"

        conn.commit()
        conn.close()
            
        
    def save(self):
        global Side

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if PrevScreen == "Edit":
            c.execute(f"UPDATE Flashcard SET Title = '{self.root.get_screen('CreateNotes').ids.Title.text}' \
                    WHERE FlashID = '{Flashcards[Index][0]}'")
            if Side == "Front":
                c.execute(f"UPDATE Flashcard SET FrontCard = '{self.root.get_screen('CreateNotes').ids.Notes.text}' \
                        WHERE FlashID = '{Flashcards[Index][0]}'")
            else:
                c.execute(f"UPDATE Flashcard SET BackCard = '{self.root.get_screen('CreateNotes').ids.Notes.text}' \
                        WHERE FlashID = '{Flashcards[Index][0]}'")
        else:
            c.execute(f"SELECT FlashID FROM Flashcard WHERE SetID = '{Set}'")
            Flashcard = c.fetchall()[-1][0]
            c.execute(f"UPDATE Flashcard SET Title = '{self.root.get_screen('CreateNotes').ids.Title.text}' \
                    WHERE FlashID = '{Flashcard}'")
            if Side == "Front":
                c.execute(f"UPDATE Flashcard SET FrontCard = '{self.root.get_screen('CreateNotes').ids.Notes.text}' \
                        WHERE FlashID = '{Flashcard}'")
            else:
                c.execute(f"UPDATE Flashcard SET BackCard = '{self.root.get_screen('CreateNotes').ids.Notes.text}' \
                        WHERE FlashID = '{Flashcard}'")

        conn.commit()
        conn.close()

    def check(self, button):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{Set}' ORDER BY FlashID DESC")
        Flashcard = c.fetchall()[0]

        if Flashcard[5] == 0:
            if Flashcard[2] == "" or Flashcard[3] == "" or Flashcard[4] == "" \
                or Flashcard[2] == None or Flashcard[3] == None or Flashcard[4] == None:
                self.root.get_screen('CreateNotes').ids.Title.text = "You have not filled in all of the required fields"
                Clock.schedule_once(Demo4.displayerror, 2)
                conn.commit()
                conn.close()
                return False
        else:
            if Flashcard[2] == "" or Flashcard[3] == "" \
                or Flashcard[2] == None or Flashcard[3] == None:
                self.root.get_screen('CreateNotes').ids.Title.text = "You have not filled in all of the required fields"
                Clock.schedule_once(Demo4.displayerror, 2)
                conn.commit()
                conn.close()
                return False
       
        if button == "Finish":
            sm.current = "Home"
        else:
            sm.current = "CreateSelection"

        c.execute(f"SELECT NumCards FROM FlashcardSet WHERE SetID = '{Set}'")
        Num = c.fetchone()[0]
        c.execute(f"UPDATE FlashcardSet SET NumCards = {Num+1} WHERE SetID = '{Set}'")

        conn.commit()
        conn.close()    

    def deleteset(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if self.root.get_screen('LearnSelection').ids.spinner_id.text == "Flashcard Set":
            self.root.get_screen('LearnSelection').ids.spinner_id.text = "No set was selected"
            Clock.schedule_once(Demo9.LoadError, 2)
            conn.commit()
            conn.close()
            return False
        c.execute(f"SELECT SetID FROM FlashcardSet WHERE SetName = '{self.root.get_screen('LearnSelection').ids.spinner_id.text}' \
                  and UserID = '{UserID}'")
        S_ID = c.fetchone()[0]
        c.execute(f"DELETE FROM FlashcardSet WHERE SetID = '{S_ID}' AND UserID = '{UserID}'")
        c.execute(f"DELETE FROM Flashcard WHERE SetID = '{S_ID}'")
        self.root.get_screen('LearnSelection').ids.spinner_id.text = "Flashcard Set"
        self.root.get_screen('LearnSelection').ids.click_label.text = "Pick the flashcard set below"

        conn.commit()
        conn.close()

    def Flag(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"SELECT Flagged FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        flag = c.fetchone()[0]

        if flag == 0:
            c.execute(f"UPDATE Flashcard SET Flagged = 1 WHERE FlashID = '{Flashcards[Index][0]}'")
            self.root.get_screen('LearnNotes').ids.FlagButton.icon = "check"
        else:
            c.execute(f"UPDATE Flashcard SET Flagged = 0 WHERE FlashID = '{Flashcards[Index][0]}'")
            self.root.get_screen('LearnNotes').ids.FlagButton.icon = "close"

        conn.commit()
        conn.close()

    def Learnt(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"SELECT Learnt FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        Learnt = c.fetchone()[0]

        if Learnt == 0:
            c.execute(f"UPDATE Flashcard SET Learnt = 1 WHERE FlashID = '{Flashcards[Index][0]}'")
            self.root.get_screen('LearnNotes').ids.LearntButton.icon = "check"
        else:
            c.execute(f"UPDATE Flashcard SET Learnt = 0 WHERE FlashID = '{Flashcards[Index][0]}'")
            self.root.get_screen('LearnNotes').ids.LearntButton.icon = "close"

        conn.commit()
        conn.close()
        
    def FlipCardLearn(self, Screen):
        global SideCard
        
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        SideCard = Flip(SideCard)
        if SideCard == "Back":
            c.execute(f"SELECT BackCard FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
            BackCard = c.fetchone()[0]
            self.root.get_screen(Screen).ids.Notes.text = BackCard
        else:
            c.execute(f"SELECT FrontCard FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
            FrontCard = c.fetchone()[0]
            self.root.get_screen(Screen).ids.Notes.text = FrontCard

        conn.commit()
        conn.close()    

    def Next(self, Screen):
        global Index, SideCard, Flashcards

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        if Screen == "Edit":
            c.execute(f"SELECT SetID FROM FlashcardSet WHERE SetName = '{self.root.get_screen('LearnSelection').ids.spinner_id.text}' \
                    and UserID = '{UserID}'")
            S_ID = c.fetchone()[0]
            c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{S_ID}'")
            Flashcards = c.fetchall()

            if len(Flashcards) == 0:
                sm.current = "LearnSelection"
                conn.commit()
                conn.close()
                return False
            
        Index += 1
        if Index == len(Flashcards):
            Index = 0

        c.execute(f"SELECT Title FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        Title = c.fetchone()[0]
        self.root.get_screen(Screen).ids.Title.text = Title

        c.execute(f"SELECT FrontCard FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        FrontCard = c.fetchone()[0]
        self.root.get_screen(Screen).ids.Notes.text = FrontCard

        c.execute(f"SELECT Format FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        Format = c.fetchone()[0]
        if Format == 1:
            self.root.get_screen(Screen).ids.Flip.disabled = True
        else:
            self.root.get_screen(Screen).ids.Flip.disabled = False

        if Screen == "LearnNotes":
            c.execute(f"SELECT Learnt FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
            Learnt = c.fetchone()[0]
            if Learnt == 1:
                self.root.get_screen(Screen).ids.LearntButton.icon = "check"
            else:
                self.root.get_screen(Screen).ids.LearntButton.icon = "close"

            c.execute(f"SELECT Flagged FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
            flag = c.fetchone()[0]
            if flag == 1:
                self.root.get_screen(Screen).ids.FlagButton.icon = "check"
            else:
                self.root.get_screen(Screen).ids.FlagButton.icon = "close"

            c.execute(f"UPDATE Flashcard SET Viewed = 1 WHERE FlashID = '{Flashcards[Index][0]}'")

        SideCard = "Front"

        conn.commit()
        conn.close()

    def Previous(self, Screen):
        global Index, SideCard

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        Index -= 1
        if Index < 0:
            Index = len(Flashcards) - 1

        c.execute(f"SELECT Title FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        Title = c.fetchone()[0]
        self.root.get_screen(Screen).ids.Title.text = Title

        c.execute(f"SELECT FrontCard FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        FrontCard = c.fetchone()[0]
        self.root.get_screen(Screen).ids.Notes.text = FrontCard

        c.execute(f"SELECT Format FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        Format = c.fetchone()[0]
        if Format == 1:
            self.root.get_screen(Screen).ids.Flip.disabled = True
        else:
            self.root.get_screen(Screen).ids.Flip.disabled = False

        if Screen == "LearnNotes":
            c.execute(f"SELECT Learnt FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
            Learnt = c.fetchone()[0]
            if Learnt == 1:
                self.root.get_screen(Screen).ids.LearntButton.icon = "check"
            else:
                self.root.get_screen(Screen).ids.LearntButton.icon = "close"

            c.execute(f"SELECT Flagged FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
            flag = c.fetchone()[0]
            if flag == 1:
                self.root.get_screen(Screen).ids.FlagButton.icon = "check"
            else:
                self.root.get_screen(Screen).ids.FlagButton.icon = "close"

            c.execute(f"UPDATE Flashcard SET Viewed = 1 WHERE FlashID = '{Flashcards[Index][0]}'")

        SideCard = "Front"

        conn.commit()
        conn.close()

    def close(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        NumCards = len(Flashcards)
        c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{Flashcards[0][1]}' AND Viewed = 1")
        Viewed = c.fetchall()
        c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{Flashcards[0][1]}' AND Flagged = 1")
        Flagged = c.fetchall()
        c.execute(f"SELECT * FROM Flashcard WHERE SetID = '{Flashcards[0][1]}' AND Learnt = 1")
        Learnt = c.fetchall()


        ProgressV = (len(Viewed)/NumCards)*100
        ProgressF = (len(Flagged)/NumCards)*100
        ProgressL = (len(Learnt)/NumCards)*100

        c.execute(f"SELECT ProgressID FROM MainProgress WHERE SetID = '{Flashcards[0][1]}'")
        P_ID = c.fetchone()[0]

        c.execute(f"SELECT ViewedID FROM ProgressViewed WHERE ProgressID = '{P_ID}' ORDER BY ViewedID ASC")
        NumViewed = c.fetchall()
        if len(NumViewed) == 10: 
            c.execute(f"DELETE FROM ProgressViewed WHERE ViewedID = '{NumViewed[0][0]}")

        c.execute(f"SELECT FlaggedID FROM ProgressFlagged WHERE ProgressID = '{P_ID}' ORDER BY FlaggedID ASC")
        NumFlagged = c.fetchall()
        if len(NumFlagged) == 10: 
            c.execute(f"DELETE FROM ProgressFlagged WHERE FlaggedID = '{NumFlagged[0][0]}")

        c.execute(f"SELECT LearntID FROM ProgressLearnt WHERE ProgressID = '{P_ID}' ORDER BY LearntID ASC")
        NumLearnt = c.fetchall()
        if len(NumLearnt) == 10: 
            c.execute(f"DELETE FROM ProgressLearnt WHERE LearntID = '{NumLearnt[0][0]}")

        timestamp = int(time.time())

        c.execute(f"INSERT INTO ProgressViewed (ProgressID, ProgressV, ViewedDate) VALUES ({P_ID}, {ProgressV}, {timestamp})")

        c.execute(f"INSERT INTO ProgressFlagged (ProgressID, ProgressF, FlaggedDate) VALUES ({P_ID}, {ProgressF}, {timestamp})")

        c.execute(f"INSERT INTO ProgressLearnt (ProgressID, ProgressL, LearntDate) VALUES ({P_ID}, {ProgressL}, {timestamp})")

        conn.commit()
        conn.close()
    
    def LatestActivity(self):
        Demo7.LatestActivity()

    def GoToSet(self, Index):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"SELECT SetName FROM FlashcardSet WHERE UserID = '{UserID}' ORDER BY LastOpened DESC")
        RecentActivity = c.fetchall()
        self.root.get_screen('LearnSelection').ids.spinner_id.text = RecentActivity[Index][0]
        sm.current = "LearnSelection"

        conn.commit()
        conn.close()

    def press(self, pressed, list_id):
        if list_id == "item1":
            self.root.get_screen('Help').ids.helpbox.text = "To change your username, you will first have to access the account page, which can be done by pressing the account button at the top of the screen. Then you can view what your current username and have the ability to change it as long it is between 1 and 30 characters and is unique."
            self.root.get_screen('Help').ids.Iconitem1.icon = "check" 
            self.root.get_screen('Help').ids.Iconitem2.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem3.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem4.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem5.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem6.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem7.icon = "minus"
        elif list_id == "item2":
            self.root.get_screen('Help').ids.helpbox.text = "To change your password, you will first have to access the account page, which can be done by pressing the account button at the top of the screen. Then you can change your password as long as it is between 12 and 30 characters, containing at least 1 capital letter, lowercase letter, number and special character"
            self.root.get_screen('Help').ids.Iconitem1.icon = "minus" 
            self.root.get_screen('Help').ids.Iconitem2.icon = "check"
            self.root.get_screen('Help').ids.Iconitem3.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem4.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem5.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem6.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem7.icon = "minus"
        elif list_id == "item3":
            self.root.get_screen('Help').ids.helpbox.text = "To change your email, you will first have to access the account page, which can be done by pressing the account button at the top of the screen. Then you can view what your current email and have the ability to change it as long it is a valid email."
            self.root.get_screen('Help').ids.Iconitem1.icon = "minus" 
            self.root.get_screen('Help').ids.Iconitem2.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem3.icon = "check"
            self.root.get_screen('Help').ids.Iconitem4.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem5.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem6.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem7.icon = "minus"
        elif list_id == "item4":
            self.root.get_screen('Help').ids.helpbox.text = "To create a flashcard, go to the create flashcard section. Then you will need to select a flashcard set, which if there is not one, then you must create one. From there you can select which format of flashcard you want."
            self.root.get_screen('Help').ids.Iconitem1.icon = "minus" 
            self.root.get_screen('Help').ids.Iconitem2.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem3.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem4.icon = "check"
            self.root.get_screen('Help').ids.Iconitem5.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem6.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem7.icon = "minus"
        elif list_id == "item5":
            self.root.get_screen('Help').ids.helpbox.text = "To learn a flashcard set, go to the learn flashcard section. Then you will need to select which set you want to learn and which type of flashcards (e.g flagged flashcards etc)."
            self.root.get_screen('Help').ids.Iconitem1.icon = "minus" 
            self.root.get_screen('Help').ids.Iconitem2.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem3.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem4.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem5.icon = "check"
            self.root.get_screen('Help').ids.Iconitem6.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem7.icon = "minus"
        elif list_id == "item6":
            self.root.get_screen('Help').ids.helpbox.text = "To edit a flashcard set, go to the learn flashcard section. Then you will need to select which flashcard set you would like to edit. Then you can scroll through the card using the next and previous buttons to either delete the card or edit the contents of the card"
            self.root.get_screen('Help').ids.Iconitem1.icon = "minus" 
            self.root.get_screen('Help').ids.Iconitem2.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem3.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem4.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem5.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem6.icon = "check"
            self.root.get_screen('Help').ids.Iconitem7.icon = "minus"
        elif list_id == "item7":
            self.root.get_screen('Help').ids.helpbox.text = "To look at your progress of the set go to the progress section. From there, select which set you would like to see your progress and which graph you would like to see from the available options: The percentage of flashcards viewed, percentage of flashcards learnt and the percenatge of flashcards flagged. This is trcaked over the last 10 sessions."
            self.root.get_screen('Help').ids.Iconitem1.icon = "minus" 
            self.root.get_screen('Help').ids.Iconitem2.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem3.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem4.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem5.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem6.icon = "minus"
            self.root.get_screen('Help').ids.Iconitem7.icon = "check"

    def EditFlashcard(self):
        global Side, Set, PrevScreen

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        PrevScreen = "Edit"

        c.execute(f"SELECT SetID FROM FlashcardSet WHERE SetName = '{self.root.get_screen('LearnSelection').ids.spinner_id.text}' \
                  and UserID = '{UserID}'")
        Set = c.fetchone()[0]

        c.execute(f"SELECT Title FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        Title = c.fetchone()[0]
        self.root.get_screen('CreateNotes').ids.Title.text = Title

        c.execute(f"SELECT FrontCard FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        FrontCard = c.fetchone()[0]
        self.root.get_screen('CreateNotes').ids.Notes.text = FrontCard

        Side = "Front"
        sm.current = "CreateNotes"

        conn.commit()
        conn.close()

    def DeleteFlashcard(self):
        global Index 

        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        c.execute(f"DELETE FROM Flashcard WHERE FlashID = '{Flashcards[Index][0]}'")
        
        c.execute(f"SELECT NumCards FROM FlashcardSet WHERE SetID = '{Flashcards[Index][1]}'")
        Num = c.fetchone()[0]
        Num -=1

        c.execute(f"UPDATE FlashcardSet SET NumCards = {Num} WHERE SetID = {Flashcards[Index][1]}")
        Index -= 1

        conn.commit()
        conn.close()

    def PlotGraph1(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        plt.clf()
        self.root.get_screen("Graph").ids.box.clear_widgets() 
        self.root.get_screen("Graph").ids.box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

        if self.root.get_screen("Progress").ids.spinner_id.text == "Flashcard Set":
            self.root.get_screen("Progress").ids.spinner_id.text = "No set was selected"
            Clock.schedule_once(Demo10.LoadError, 2)
            conn.commit()
            conn.close()
            return False

        sm.current = "Graph"

        c.execute(f"SELECT SetID FROM FlashcardSet WHERE SetName = '{self.root.get_screen('Progress').ids.spinner_id.text}' \
                   AND UserID = '{UserID}'")
        SetId = c.fetchone()[0]
        c.execute(f"SELECT ProgressID FROM MainProgress WHERE SetID = '{SetId}'")
        P_ID = c.fetchone()[0]

        c.execute(f"SELECT ProgressV FROM ProgressViewed WHERE ProgressID = '{P_ID}' ORDER BY ViewedID ASC")
        Viewed = c.fetchall()

        c.execute(f"SELECT ViewedDate FROM ProgressViewed WHERE ProgressID = '{P_ID}' ORDER BY ViewedID ASC")
        Times = c.fetchall()
        Dates = []
        for Time in range(len(Times)):
            Dates.append(datetime.datetime.fromtimestamp(int(f"{Times[Time][0]}")).strftime('%d-%m-%Y %H:%M:%S'))
        
        x = [1,2,3,4,5,6,7,8,9,10]
        y = []

        for Card in range(len(Viewed)):
            y.append(Viewed[Card][0])

        Percenatages = sorted(y)
        Max = Percenatages[-1]
        Min = Percenatages[0]
        Avg = sum(Percenatages)/len(Percenatages)
        
        while len(y) != 10:
            y.append(0)

        while len(Dates) != 10:
            Dates.append("None")


        plt.plot(x,y)
        plt.ylabel("Percentage Viewed")
        plt.xlabel("Sessions")
        plt.title("Percentage of flashcards viewed in the set")

        self.root.get_screen("Graph").ids.Highest.text = f"The highest percentage is {Max}%"
        self.root.get_screen("Graph").ids.Lowest.text = f"The lowest percentage is {Min}%"
        self.root.get_screen("Graph").ids.Average.text = f"The average percentage is {Avg}%"

        self.root.get_screen("Graph").ids.Session1.text = f"Session 1: {Dates[0]}"
        self.root.get_screen("Graph").ids.Session2.text = f"Session 2: {Dates[1]}"
        self.root.get_screen("Graph").ids.Session3.text = f"Session 3: {Dates[2]}"
        self.root.get_screen("Graph").ids.Session4.text = f"Session 4: {Dates[3]}"
        self.root.get_screen("Graph").ids.Session5.text = f"Session 5: {Dates[4]}"
        self.root.get_screen("Graph").ids.Session6.text = f"Session 6: {Dates[5]}"
        self.root.get_screen("Graph").ids.Session7.text = f"Session 7: {Dates[6]}"
        self.root.get_screen("Graph").ids.Session8.text = f"Session 8: {Dates[7]}"
        self.root.get_screen("Graph").ids.Session9.text = f"Session 9: {Dates[8]}"
        self.root.get_screen("Graph").ids.Session10.text = f"Session 10: {Dates[9]}"
    

        conn.commit()
        conn.close()

    def PlotGraph2(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        plt.clf()
        self.root.get_screen("Graph").ids.box.clear_widgets() 
        self.root.get_screen("Graph").ids.box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

        if self.root.get_screen("Progress").ids.spinner_id.text == "Flashcard Set":
            self.root.get_screen("Progress").ids.spinner_id.text = "No set was selected"
            Clock.schedule_once(Demo10.LoadError, 2)
            conn.commit()
            conn.close()
            return False

        sm.current = "Graph"
         
        c.execute(f"SELECT SetID FROM FlashcardSet WHERE SetName = '{self.root.get_screen('Progress').ids.spinner_id.text}' \
                   AND UserID = '{UserID}'")
        SetId = c.fetchone()[0]
        c.execute(f"SELECT ProgressID FROM MainProgress WHERE SetID = '{SetId}'")
        P_ID = c.fetchone()[0]

        c.execute(f"SELECT ProgressF FROM ProgressFlagged WHERE ProgressID = '{P_ID}' ORDER BY FlaggedID ASC")
        Flagged = c.fetchall()

        c.execute(f"SELECT FlaggedDate FROM ProgressFlagged WHERE ProgressID = '{P_ID}' ORDER BY FlaggedID ASC")
        Times = c.fetchall()
        Dates = []
        for Time in range(len(Times)):
            Dates.append(datetime.datetime.fromtimestamp(int(f"{Times[Time][0]}")).strftime('%d-%m-%Y %H:%M:%S'))

        x = [1,2,3,4,5,6,7,8,9,10]
        y = []

        for Card in range(len(Flagged)):
            y.append(Flagged[Card][0])

        Percenatages = sorted(y)
        Max = Percenatages[-1]
        Min = Percenatages[0]
        Avg = sum(Percenatages)/len(Percenatages)

        while len(y) != 10:
            y.append(0)

        while len(Dates) != 10:
            Dates.append("None")
                    
        plt.plot(x,y)
        plt.ylabel("Percentage Flagged")
        plt.xlabel("Sessions")
        plt.title("Percentage of flashcards flagged in the set")

        self.root.get_screen("Graph").ids.Highest.text = f"The highest percentage is {Max}%"
        self.root.get_screen("Graph").ids.Lowest.text = f"The lowest percentage is {Min}%"
        self.root.get_screen("Graph").ids.Average.text = f"The average percentage is {Avg}%"

        self.root.get_screen("Graph").ids.Session1.text = f"Session 1: {Dates[0]}"
        self.root.get_screen("Graph").ids.Session2.text = f"Session 2: {Dates[1]}"
        self.root.get_screen("Graph").ids.Session3.text = f"Session 3: {Dates[2]}"
        self.root.get_screen("Graph").ids.Session4.text = f"Session 4: {Dates[3]}"
        self.root.get_screen("Graph").ids.Session5.text = f"Session 5: {Dates[4]}"
        self.root.get_screen("Graph").ids.Session6.text = f"Session 6: {Dates[5]}"
        self.root.get_screen("Graph").ids.Session7.text = f"Session 7: {Dates[6]}"
        self.root.get_screen("Graph").ids.Session8.text = f"Session 8: {Dates[7]}"
        self.root.get_screen("Graph").ids.Session9.text = f"Session 9: {Dates[8]}"
        self.root.get_screen("Graph").ids.Session10.text = f"Session 10: {Dates[9]}"

        conn.commit()
        conn.close()

    def PlotGraph3(self):
        conn = sqlite3.connect("Flashcard_App.db")
        c = conn.cursor()

        plt.clf()
        self.root.get_screen("Graph").ids.box.clear_widgets() 
        self.root.get_screen("Graph").ids.box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

        if self.root.get_screen("Progress").ids.spinner_id.text == "Flashcard Set":
            self.root.get_screen("Progress").ids.spinner_id.text = "No set was selected"
            Clock.schedule_once(Demo10.LoadError, 2)
            conn.commit()
            conn.close()
            return False

        sm.current = "Graph"

        c.execute(f"SELECT SetID FROM FlashcardSet WHERE SetName = '{self.root.get_screen('Progress').ids.spinner_id.text}' \
                   AND UserID = '{UserID}'")
        SetId = c.fetchone()[0]
        c.execute(f"SELECT ProgressID FROM MainProgress WHERE SetID = '{SetId}'")
        P_ID = c.fetchone()[0]

        c.execute(f"SELECT ProgressL FROM ProgressLearnt WHERE ProgressID = '{P_ID}' ORDER BY LearntID ASC")
        Learnt = c.fetchall()

        c.execute(f"SELECT LearntDate FROM ProgressLearnt WHERE ProgressID = '{P_ID}' ORDER BY LearntID ASC")
        Times = c.fetchall()
        Dates = []
        for Time in range(len(Times)):
            Dates.append(datetime.datetime.fromtimestamp(int(f"{Times[Time][0]}")).strftime('%d-%m-%Y %H:%M:%S'))

        x = [1,2,3,4,5,6,7,8,9,10]
        y = []

        for Card in range(len(Learnt)):
            y.append(Learnt[Card][0])

        Percenatages = sorted(y)
        Max = Percenatages[-1]
        Min = Percenatages[0]
        Avg = sum(Percenatages)/len(Percenatages)
        
        while len(y) != 10:
            y.append(0)

        while len(Dates) != 10:
            Dates.append("None")

        plt.plot(x,y)
        plt.ylabel("Percentage Learnt")
        plt.xlabel("Sessions")
        plt.title("Percentage of flashcards learnt in the set")

        self.root.get_screen("Graph").ids.Highest.text = f"The highest percentage is {Max}%"
        self.root.get_screen("Graph").ids.Lowest.text = f"The lowest percentage is {Min}%"
        self.root.get_screen("Graph").ids.Average.text = f"The average percentage is {Avg}%"

        self.root.get_screen("Graph").ids.Session1.text = f"Session 1: {Dates[0]}"
        self.root.get_screen("Graph").ids.Session2.text = f"Session 2: {Dates[1]}"
        self.root.get_screen("Graph").ids.Session3.text = f"Session 3: {Dates[2]}"
        self.root.get_screen("Graph").ids.Session4.text = f"Session 4: {Dates[3]}"
        self.root.get_screen("Graph").ids.Session5.text = f"Session 5: {Dates[4]}"
        self.root.get_screen("Graph").ids.Session6.text = f"Session 6: {Dates[5]}"
        self.root.get_screen("Graph").ids.Session7.text = f"Session 7: {Dates[6]}"
        self.root.get_screen("Graph").ids.Session8.text = f"Session 8: {Dates[7]}"
        self.root.get_screen("Graph").ids.Session9.text = f"Session 9: {Dates[8]}"
        self.root.get_screen("Graph").ids.Session10.text = f"Session 10: {Dates[9]}"

        conn.commit()
        conn.close()

if __name__ == "__main__":
    MainApp().run()
'''
        c.execute("SELECT * FROM Flashcard")
        result = c.fetchall()
        for row in result:
            print(row)'''
