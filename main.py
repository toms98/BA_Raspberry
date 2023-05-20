from tkinter import*

def button_action():
    anweisungs_label.config(text="Ich wurde geändert!")

def entry_action():
    entry_text = eingabefeld.get()
    if (entry_text == ""):
        welcome_label.config(text="Gib zuerst einen Namen ein.")
    else:
        entry_text = "Welcome " + entry_text + "!"
        welcome_label.config(text=entry_text)

fenster = Tk()
fenster.title("Nur ein Fenster")

my_label = Label(fenster, text="Gib einen Namen ein: ")

welcome_label = Label(fenster)

eingabefeld = Entry(fenster, bd=5, width=40)

welcome_button = Button(fenster, text="Click me", command=entry_action)
change_button = Button(fenster, text="Ändern", command=button_action)
exit_button = Button(fenster, text="Beenden", command=fenster.quit)

anweisungs_label = Label(fenster, text="Ich bin eine Anweisung:\n\
Klicke auf 'Ändern'.")
info_label = Label(fenster, text="Ich bin eine Info \n\
Der Beenden Button schließt das Programm.")

fenster.geometry("450x400")

my_label.grid(row=0, column=0)
eingabefeld.grid(row=0, column=1)
welcome_button.grid(row=1, column=0)
welcome_label.grid(row=2, column=0, columnspan=2)

"""
anweisungs_label.place(x=0, y=0, width=200, height=150)
change_button.place(x=220, y=0, width=200, height=150)
info_label.place(x=100, y=160, width=300, height=100)
exit_button.place(x=100, y=260, width=300, height=100)
"""

anweisungs_label.grid(row=4, column=0, pady=20)
change_button.grid(row=5, column=1, pady=20)
info_label.grid(row=6, column=0)
exit_button.grid(row=7, column=1)

fenster.mainloop()
