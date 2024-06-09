import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Progressbar
import wikipedia  # Import the Wikipedia library
import os
import pyttsx3
from PyPDF2 import PdfReader
import sqlite3
import random
import string

conn = sqlite3.connect('texttospeech.db')
procces = conn.cursor()
conn.commit()
table = procces.execute("create table if not exists texts(speechtext text, filename text)")

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech")
        self.root.geometry("900x450+200+200")
        self.root.resizable(False, False)
        self.root.configure(bg="#696969")
       
        # Initialize the text-to-speech engine
        self.engine = pyttsx3.init()

        self.create_widgets()

        # Initialize history list
        self.history = []

    def create_widgets(self):
        self.Top_Frame = Frame(self.root, bg="#d3d3d3", width=1000, height=100)
        self.Top_Frame.place(x=0, y=0)

        self.Logo = PhotoImage(file="icon1.png")
        Label(self.Top_Frame, image=self.Logo, bg="#d3d3d3").place(x=-5, y=-30)

        Label(self.Top_Frame, text="Text to Speech", font="arial 25 bold", bg="#d3d3d3", fg="black").place(x=135, y=30)

        self.text_area = Text(self.root, font="Roboto 20", bg="white", relief=GROOVE, wrap=WORD)
        self.text_area.place(x=10, y=150, width=500, height=250)

        Label(self.root, text="SPEED", font="arial 15 bold", bg="#696969", fg="white").place(x=670, y=160)

        self.speed_combobox = Combobox(self.root, values=['Fast', 'Normal', 'Slow'], font="arial 14", state='readonly', width=10)
        self.speed_combobox.place(x=640, y=200)
        self.speed_combobox.set('Normal')

        self.btn_speak = Button(self.root, text="SPEAK", width=10, height=2, bg="#d3d3d3", font="arial 14 bold ",
                                command=self.speaknow, relief=RAISED)
        self.btn_speak.place(x=550, y=250)
        self.btn_save = Button(self.root, text="SAVE", width=10, height=2, bg="#d3d3d3", font="arial 14 bold ",
                               command=self.download, relief=RAISED)
        self.btn_save.place(x=730, y=250)
        self.btn_pdf = Button(self.root, text="OPEN PDF", width=10, height=2, bg="#d3d3d3", font="arial 14 bold ",
                              command=self.open_pdf, relief=RAISED)
        self.btn_pdf.place(x=550, y=350)
        self.btn_mode = Button(self.root, text="INFO", width=10, height=2, bg="#d3d3d3", font="arial 14 bold",
                               command=self.get_wikipedia_info, relief=RAISED)
        self.btn_mode.place(x=730, y=350)
        self.btn_clear = Button(self.root, text="CLEAR", width=7, height=1, bg="#d3d3d3", font="arial 14 bold",
                            command=self.clear_text_area, relief=RAISED)
        self.btn_clear.place(x=417, y=106)

    def clear_text_area(self):
        # Clear the text area
        self.text_area.delete(1.0, END)

    def speaknow(self):
        text = self.text_area.get(1.0, END)
        speed = self.speed_combobox.get()

        if text:

            if speed == 'Fast':
                self.engine.setProperty('rate', 250)
            elif speed == 'Normal':
                self.engine.setProperty('rate', 150)
            else:
                self.engine.setProperty('rate', 60)

            # Speak the text
            self.engine.say(text)
            self.engine.runAndWait()

    def addtext(self):
        text = self.text_area.get(1.0, END)

    @staticmethod
    def random_string(length=5):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for _ in range(length))

    def download(self):
        text = self.text_area.get(1.0, END)
        speed = self.speed_combobox.get()
        random_str = self.random_string()
        add = "insert into texts (speechtext, filename) values(?,?)"
        procces.execute(add, (text, random_str))
        conn.commit()

        # Save text to file with selected voice and speed
        if text:
            path = filedialog.askdirectory()
            os.chdir(path)
            self.engine.save_to_file(text, random_str + ".mp3")
            self.engine.runAndWait()

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            self.text_area.delete(1.0, END)
            self.text_area.insert(END, text)

    def get_wikipedia_info(self):
        query = self.text_area.get(1.0, END)
        try:
            # Get information from Wikipedia
            result = wikipedia.summary(query, sentences=2)

            # Display the information in the text area
            self.text_area.delete(1.0, END)
            self.text_area.insert(END, result)
        except wikipedia.exceptions.DisambiguationError as e:
            # If the query is ambiguous, display a message
            messagebox.showwarning("Ambiguous Query", f"Multiple results found for '{query}'. Please refine your search.")
        except wikipedia.exceptions.PageError as e:
            # If the query doesn't match any Wikipedia page, display a message
            messagebox.showerror("Page Not Found", f"No Wikipedia page found for '{query}'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
