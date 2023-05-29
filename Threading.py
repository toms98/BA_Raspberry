from tkinter import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
import numpy as np
from drawnow import *
import threading
from time import sleep

# Globale Variable
global scaler_x  # X-Achsen Skalierung
scaler_x = 1

global scaler_y  # Y-Achsen Skalierung
scaler_y = 5

global trigger  # Variable für Triggerschwelle
trigger = 0.0

global data  # Variable in die ausgelesene Daten geschrieben werden
data = 0

global event  # Event für Threading Prozess
event = threading.Event()

global data_rx_x  # Array für Daten auf der x-Achse
data_rx_x = []

global data_rx_y  # Array für Daten auf der y-Achse
data_rx_y = []

global counter
counter = -scaler_x

global time
time = 860  # Samples per Second des Microcontrollers

global checker
checker = False


# Button-Actions
def auto_trigger_action():  # todo
    fenster.quit()


def time_update_action():
    global scaler_x
    scaler_x = float(time_spinbox.get())
    stop_button_action()
    reset_button_action()
    start_button_action()
    makeFig()


def volt_update_action():
    global scaler_y
    scaler_y = float(volt_spinbox.get())
    stop_button_action()
    reset_button_action()
    start_button_action()
    makeFig()


def trigger_update_action():
    global trigger
    trigger = float(trigger_spinbox.get())
    stop_button_action()
    reset_button_action()
    start_button_action()
    makeFig()


def windowClose():
    global event
    event.set()
    fenster.destroy()


def readLine():
    # später hier Datenstream des ADC auslesen und übergeben
    global data
    datei = open('./rng.txt', 'r')
    data = (float(datei.readline().strip()) / 8000) - 4.096  # Speichern der eingelesenen Zeile auf globale data-Variable
    datei.close()


def add_data_action():
    global data_rx_x
    global data_rx_y
    global data
    global counter
    global time
    global scaler_x

    # Einordnen der Zeitwerte in das Array - Schrittweite = time = 1/SPS
    data_rx_x.append(float(counter))
    counter = counter + (1 / time)

    # Einordnen der Datenwerte in das Array
    # counter_y = data  # Umrechnung Bit-Wert in Volt
    data_rx_y.append(data)

    # print("Counter y: ", counter_y)
    # print("Array x: ", data_rx_x)
    # print("Array y: ", data_rx_y)


def data_retrieve_action(event):
    # aktualisieren des Labels bei Knopfdruck
    global trigger
    global data
    global checker
    data_old = 0.0
    has_data_old = False

    while (True):
        if event.is_set():
            event.clear()
            break

        has_data_old = False

        if checker == True:
            # for x in range(int(time * (scaler_x * 2))):
            #     readLine()
            #     data2 = round((float(data) / 8000) - 4.096)
            #     if data2 == int(trigger):
            #         readLine()
            #         add_data_action()
            #         change_action()
            #         #x += 1
            #         makeFig()
            #     else:
            #         change_action()
            #         #print(data)

            for x in range(int(time * (scaler_x * 2))):
                readLine()
                # print(round(data, 2), " - ", trigger, " - ", round(data_old, 2))
                if not has_data_old:
                    data_old = data
                    has_data_old = True
                    change_action()
                    continue
                if (data >= trigger >= data_old) or (data <= trigger <= data_old):
                    makeFig()
                add_data_action()
                change_action()

                data_old = data

            #print("Data: ", data2)
            print("Trigger:", trigger)
        else:
            for x in range(int(time * (scaler_x * 2))):
                readLine()
                add_data_action()
                change_action()
            makeFig()
        #
        #
        #
        # for x in range(int(time * (scaler_x * 2))):
        #     readLine()
        #     add_data_action()
        #     change_action()
        #     x += 1
        #
        # makeFig()


def start_button_action():
    global thread
    global event
    thread = threading.Thread(target=data_retrieve_action, args=(event,))
    thread.do_run = True
    thread.start()


def stop_button_action():
    # Stoppen des Auslese-Threads
    global event
    event.set()


def reset_button_action():
    # Zurücksetzen aller Variablen und updaten des Graphen
    global data_rx_x
    global data_rx_y
    global counter
    data_rx_x = []
    data_rx_y = []
    counter = -scaler_x
    makeFig()


def trigger_button_action():
    global checker
    if not checker:
        checker = True
    else:
        checker = False
    print(checker)


def change_action():
    # rotierender Austausch der Zeilen im Dokument mit Beispielwerten
    with open('./rng.txt', 'r') as fr:
        lines = fr.readlines()
        zeile = lines[0]
        ptr = 0

        with open('./rng.txt', 'w+') as fw:
            for line in lines:
                if ptr != 0:
                    fw.write(line)
                ptr += 1
    f = open('./rng.txt', 'a')
    f.write(zeile)
    f.close()


# Erstellen des Graphen
def makeFig():
    global counter
    global data_rx_x
    global data_rx_y

    # Festlegen der Größe des Plots
    fig = Figure(dpi=100)
    fig.set_figwidth(6.25)
    fig.set_figheight(4)

    ax = fig.add_subplot(111)  # Erstellen des Graphen im Plot
    ax.plot(data_rx_x, data_rx_y, 'g')  # Hinzufügen des Graphen mit Werten der data-Arrays
    ax.axhline(y=trigger, color='r')  # rote horizontale Linie für Triggerschwelle
    ax.set_xlim(-scaler_x, scaler_x)  # Festlegen der Randwerte der x-Achse
    ax.set_ylim(-scaler_y, scaler_y)  # Festlegen der Randwerte der y-Achse

    canvas = FigureCanvasTkAgg(fig, master=fenster)
    canvas.draw()

    if counter >= scaler_x:
        data_rx_x = []
        data_rx_y = []
        counter = -scaler_x

    canvas.get_tk_widget().place(x=175, y=30)


# Fenster erstellen
fenster = Tk()
fenster.title("Window with Plot")  # Name des Fensters
fenster.configure(background="white")

# plt.rcParams['toolbar'] = 'None' #anscheinend unnötig bei canvas

# Labels
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

trigger_button_label = Label(fenster, text="Trigger", bg="#FFF", fg="#000", font="Oswald, 8")

text_label = Label(fenster, text=data, bg="#FFF", fg="#000", font="Oswald, 18")

# Buttons
auto_trigger_button = Button(fenster, text="AUTO-Trigger", command=auto_trigger_action, bg="#FFF", fg="#000",
                             height="1", width="8")
exit_button = Button(fenster, text="Beenden", command=windowClose, bg="#FFF", fg="#000", height="1", width="4")

start_button = Button(fenster, text="Start", command=start_button_action, bg="#FFF", fg="#000", height="1", width="4")
stop_button = Button(fenster, text="Stop", command=stop_button_action, bg="#FFF", fg="#000", height="1", width="4")
reset_button = Button(fenster, text="Reset", command=reset_button_action, bg="#FFF", fg="#000", height="1", width="4")

# Spinboxes
volt_str = StringVar(fenster)
time_str = StringVar(fenster)
tri_str = StringVar(fenster)
volt_str.set(str(scaler_y))
time_str.set(str(scaler_x))
tri_str.set(str(trigger))

volt_spinbox = Spinbox(fenster, background="white", width=4, from_=1, to=5, increment=1, font="Oswald, 18", fg="#000",
                       bg="#FFF", command=volt_update_action, textvariable=volt_str)
time_spinbox = Spinbox(fenster, background="white", width=4, from_=1, to=10, increment=1, font="Oswald, 18", fg="#000",
                       bg="#FFF", command=time_update_action, textvariable=time_str)
trigger_spinbox = Spinbox(fenster, background="white", width=4, from_=-10, to=10, increment=1, font="Oswald, 18",
                          fg="#000", bg="#FFF", command=trigger_update_action, textvariable=tri_str)

# Checkbox
trigger_checkbox = Checkbutton(fenster, variable=checker, background="white", font="Oswald, 18", fg="#000", bg="#FFF",
                               command=trigger_button_action)

# Window
fenster.geometry("800x480")

# Orientation
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
reset_button.place(x=15, y=360)

auto_trigger_button.place(x=15, y=270)
trigger_checkbox.place(x=90, y=260)

cur_fre_label.place(x=35, y=390)
cur_per_label.place(x=35, y=420)
cur_vol_label.place(x=35, y=450)

frequency_label.place(x=65, y=390)
period_label.place(x=65, y=420)
cursor_label.place(x=65, y=450)

trigger_button_label.place(x=120, y=270)

# canvas.get_tk_widget().place(x=175, y=30)
exit_button.place(x=730, y=450)

# Main
makeFig()
fenster.mainloop()
