from tkinter import *
from tkinter import messagebox

def button_action():
    print("Ich wurde über das Menü ausgeführt.")

def action_get_info_dialog():
    m_text = "\
    ****************************\n\
    Autor: Hans Mustermann\n\
    Date: 16.06.16\n\
    Version: 1.06\n\
    ****************************"
    messagebox.showinfo(message=m_text, title="Infos")

fenster = Tk()
fenster.title("Programm mit einem Menü")

info_text = Label(fenster, text ="Ich habe ein Menü!\n\
Wenn du darauf Klickst geht ein Drop-Down-Menü auf.")
info_text.pack()

menuleiste = Menu(fenster)

datei_menu = Menu(menuleiste, tearoff=0)
help_menu = Menu(menuleiste, tearoff=0)

datei_menu.add_command(label="Anwenden", command=button_action)
datei_menu.add_separator()
datei_menu.add_command(label="Exit", command=fenster.quit)

help_menu.add_command(label="Info!", command=action_get_info_dialog)

menuleiste.add_cascade(label="Datei", menu=datei_menu)
menuleiste.add_cascade(label="Help", menu=help_menu)

fenster.config(menu=menuleiste)

fenster.mainloop()
