from tkinter import*
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
import numpy as np
from drawnow import *
import threading

#Globale Variable
global scaler_x
scaler_x = 1

global scaler_y
scaler_y = 10

global trigger
trigger = 1.0

global data
data = 0

#Daten für Plot
data_x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
data_y = [4.0, 7.0, 1.0, 9.0, 5.0, 2.0, 8.0]

#Button-Actions
def auto_trigger_action(): fenster.quit()

def time_update_action():
    global scaler_x
    scaler_x = float(time_spinbox.get())
    makeFig()

def volt_update_action():
    global scaler_y
    scaler_y = float(volt_spinbox.get())
    makeFig()

def trigger_update_action():
    global trigger
    trigger = float(trigger_spinbox.get())
    makeFig()

#Fenster erstellen
fenster = Tk()
fenster.title("Window with Plot")
fenster.configure(background="white")

def readLine():
    #später hier Datenstream des ADC auslesen und übergeben
    global data
    datei = open('/Users/tomschroeter/Desktop/rng.txt', 'r')
    daten = datei.readline().strip()
    datei.close()
    #print(daten)

def data_retrieve_action():

    # aktualisieren des Labels bei Knopfdruck
    while (True):
        readLine()
        text_label.config(text=data)
        makeFig()
        change_action()

def start_button_action():
    global thread
    thread = threading.Thread(target=data_retrieve_action)
    thread.do_run = True
    thread.start()

def stop_button_action():

    thread.do_run = False
    thread.join()

def change_action():
    with open('/Users/tomschroeter/Desktop/rng.txt', 'r') as fr:
        lines = fr.readlines()
        zeile = lines[0]
        ptr = 0

        with open('/Users/tomschroeter/Desktop/rng.txt', 'w+') as fw:
            for line in lines:
                if ptr != 0:
                    fw.write(line)
                ptr += 1
    f = open('/Users/tomschroeter/Desktop/rng.txt', 'a')
    f.write(zeile)
    f.close()

#Erstellen des Graphen
def makeFig():
    fig = Figure(dpi=100)
    fig.set_figwidth(6.25)
    fig.set_figheight(4)

    ax = fig.add_subplot(111)
    ax.plot(data_x, data_y, 'g')
    ax.axhline(y=trigger, color='r')
    ax.set_xlim(0, scaler_x)
    ax.set_ylim(0, scaler_y)

    canvas = FigureCanvasTkAgg(fig, master=fenster)
    canvas.draw()

    canvas.get_tk_widget().place(x=175, y=30)


#plt.rcParams['toolbar'] = 'None' #anscheinend unnötig bei canvas

#Labels
headline_label = Label(fenster, text="Oszilloskop", bg="#BFF524", fg="#000", font="Oswald, 18")

voltage_label = Label(fenster, text="Volts/Div", bg="#FFF", fg="#000", font="Oswald, 18")
time_label = Label(fenster, text="Time/Div", bg="#FFF", fg="#000", font="Oswald, 18")
trigger_label = Label(fenster, text="Trigger/V", bg="#FFF", fg="#000", font="Oswald, 18")
frequency_label = Label(fenster, text="f/Hz", bg="#FFF", fg="#000", font="Oswald, 24")
period_label = Label(fenster, text="T/ms", bg="#FFF", fg="#000", font="Oswald, 24")
cursor_label = Label(fenster, text="mV", bg="#FFF", fg="#000", font="Oswald, 24")

cur_fre_label = Label(fenster, text="0", bg="#FFF", fg="#000", font="Oswald, 24")
cur_per_label = Label(fenster, text="0", bg="#FFF", fg="#000", font="Oswald, 24")
cur_vol_label = Label(fenster, text="0", bg="#FFF", fg="#000", font="Oswald, 24")

text_label = Label(fenster, text=data, bg="#FFF", fg="#000", font="Oswald, 18")

#Buttons
auto_trigger_button = Button(fenster, text="AUTO-Trigger", command= auto_trigger_action, bg="#FFF", fg="#000", height="1", width="8")
exit_button = Button(fenster, text="Beenden", command=fenster.quit, bg="#FFF", fg="#000", height="1", width="4")

start_button = Button(fenster, text="Start", command=start_button_action, bg="#FFF", fg="#000", height="1", width="4")
stop_button = Button(fenster, text="Stop", command=stop_button_action, bg="#FFF", fg="#000", height="1", width="4")

#Spinboxes
volt_str = StringVar(fenster)
time_str = StringVar(fenster)
tri_str = StringVar(fenster)
volt_str.set(str(scaler_y))
time_str.set(str(scaler_x))
tri_str.set(str(trigger))

volt_spinbox = Spinbox(fenster, background="white", width=4, from_=1, to=10, increment=1, font="Oswald, 18", fg="#000", bg="#FFF", command=volt_update_action, textvariable=volt_str)
time_spinbox = Spinbox(fenster, background="white", width=4, from_=1, to=10, increment=1, font="Oswald, 18", fg="#000", bg="#FFF", command=time_update_action, textvariable=time_str)
trigger_spinbox = Spinbox(fenster, background="white", width=4, from_=0, to=10, increment=1, font="Oswald, 18", fg="#000", bg="#FFF", command=trigger_update_action, textvariable=tri_str)

#Window
fenster.geometry("800x480")

#Orientation
headline_label.place(x=0, y=0)

volt_spinbox.place(x=15, y=90)
time_spinbox.place(x=15, y=150)
trigger_spinbox.place(x=15, y=210)

voltage_label.place(x=90, y=90)
time_label.place(x=90, y=150)
trigger_label.place(x=90, y=210)

start_button.place(x=15, y=300)
text_label.place(x=90, y=300)
stop_button.place(x=15, y=330)

auto_trigger_button.place(x=15, y=270)

cur_fre_label.place(x=35, y=390)
cur_per_label.place(x=35, y=420)
cur_vol_label.place(x=35, y=450)

frequency_label.place(x=65, y=390)
period_label.place(x=65, y=420)
cursor_label.place(x=65, y=450)

#canvas.get_tk_widget().place(x=175, y=30)
exit_button.place(x=730, y=450)

#Main
makeFig()
while (True):
    fenster.mainloop()
