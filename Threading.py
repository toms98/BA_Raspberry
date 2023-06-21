from tkinter import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
import numpy as np
from drawnow import *
import threading
import time
import queue


class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


# Globale Variable
global scaler_x  # X-Achsen Skalierung
scaler_x = 0.5

global scaler_y  # Y-Achsen Skalierung
scaler_y = 3

global triggerValue  # Variable für Triggerschwelle
triggerValue = 0.0

global event  # Event für Threading Prozess
event = threading.Event()

# global data_rx_x  # Array für Daten auf der x-Achse
# data_rx_x = []
#
# global data_rx_y  # Array für Daten auf der y-Achse
# data_rx_y = []
#
# global counter
# counter = -scaler_x

global samplePerSecond
samplePerSecond = 860  # Samples per Second des Microcontrollers

global checker
checker = False
global data_x
data_x = []
global data_y
data_y = []
global isRunning
isRunning = False
global thread

global q
q = queue.Queue()
global timer

# Button-Actions
def auto_trigger_action():  # todo
    fenster.quit()


def time_update_action():
    global scaler_x
    global data_x
    global data_y
    global isRunning
    scaler_x = float(time_spinbox.get())
    data_x.clear()
    for i in range(round(-scaler_x * 2 * samplePerSecond), round(scaler_x * 2 * samplePerSecond)):
        data_x.append(i / samplePerSecond)
    data_y = data_y[-len(data_x):]
    if not isRunning:
        makeFig()


def volt_update_action():
    global scaler_y
    global isRunning
    scaler_y = float(volt_spinbox.get())
    if not isRunning:
        makeFig()


def trigger_update_action():
    global triggerValue
    trigger = float(trigger_spinbox.get())
    if not isRunning:
        makeFig()


def windowClose():
    global event
    event.set()
    fenster.destroy()


global textDaten
textDaten = None
global counterDaten
counterDaten = 0


def readLine():
    global textDaten
    global counterDaten
    name = "./rng.txt"
    if textDaten is None:
        datei = open(name, 'r')
        textDaten = []
        for l in datei.readlines():
            textDaten.append((float(l.strip()) / 8000) - 4.096)

    data = textDaten[counterDaten]
    counterDaten += 1
    if counterDaten == len(textDaten):
        counterDaten = 0
    return data


def readLine3():
    global q
    global textDaten
    global counterDaten
    global tlast
    print(time.time()- tlast)
    tlast = time.time()
    name = "./rng.txt"
    if textDaten is None:
        print(1)
        datei = open(name, 'r')
        textDaten = []
        for l in datei.readlines():
            textDaten.append((float(l.strip()) / 8000) - 4.096)

    data = textDaten[counterDaten]
    counterDaten += 1
    if counterDaten == len(textDaten):
        counterDaten = 0#
    q.put(data)


def mainThread():
    # aktualisieren des Labels bei Knopfdruck
    global triggerValue
    global checker
    global scaler_x
    global isRunning
    global q
    global timer
    data_old = None
    is_triggered = False

    # todo
    global data_x
    global data_y

    POINTS_TOGETHER = 100

    time_update_action()

    counter = 0
    q = queue.Queue()
    timer = RepeatTimer(0.001, readLine3)
    timer.start()
    global tlast

    t1 = 0
    while (True):
        if event.is_set():
            event.clear()
            break
        # data = readLine2()
        data = q.get()
        # Trigger
        if checker:
            if is_triggered:
                data_y.append(data)
                if counter == 0:
                    makeFig()
                counter += 1
                counter %= POINTS_TOGETHER
                if len(data_x) == len(data_y):
                    makeFig()
                    break
            else:
                if data_old is None:
                    data_old = data
                elif (data >= trigger >= data_old) or (data <= trigger <= data_old):
                    data_old = None
                    data_y.append(data)
                    is_triggered = True
                else:
                    data_old = data
                data_y.append(data)
                if len(data_y) > scaler_x * samplePerSecond / 2:
                    data_y.remove(data_y[0])
                if counter == 0:
                    makeFig()
                counter += 1
                counter %= POINTS_TOGETHER


        # nicht Trigger
        else:
            data_y.append(data)
            if len(data_y) == len(data_x):
                makeFig()
                data_y = []
                print("ges:", time.time() - t1)
                t1 = time.time()
            # if len(data_y) > len(data_x):
            #    data_y.remove(data_y[0])
            # if counter == 0:
            #    makeFig()
            #    print(time.time()-t1)
            #    t1 = time.time()
            # counter += 1
            # counter %= POINTS_TOGETHER
    isRunning = False
    timer.cancel()


def start_button_action():
    global event
    global isRunning
    global thread
    global checker
    if isRunning:
        return
    if checker:
        reset_button_action()
    event.clear()
    isRunning = True
    thread = threading.Thread(target=mainThread)
    thread.do_run = True
    thread.start()


def stop_button_action():
    # Stoppen des Auslese-Threads
    global event
    global isRunning
    global thread
    global timer
    event.set()
    isRunning = False
    timer.cancel()


def reset_button_action():
    # Zurücksetzen aller Variablen und updaten des Graphen
    global data_x
    global data_y
    global fig
    global event
    global isRunning
    stop_button_action()
    data_x.clear()
    data_y.clear()
    subplot.clear()
    subplot.set_xlim(-scaler_x * 2, scaler_x * 2)  # Festlegen der Randwerte der x-Achse
    subplot.set_ylim(-scaler_y * 2, scaler_y * 2)  # Festlegen der Randwerte der y-Achse
    subplot.axhline(y=triggerValue, color='r')  # rote horizontale Linie für Triggerschwelle
    fig.canvas.draw()


def trigger_button_action():
    global checker
    if not checker:
        checker = True
    else:
        checker = False
    stop_button_action()
    reset_button_action()


global tlast
tlast = time.time()


def makeFig():
    global data_x
    global data_y
    global subplot
    global fig
    global event

    fig.delaxes(subplot)
    subplot = fig.add_subplot(111)
    data_y_tmp = data_y
    if len(data_y) > len(data_x):
        data_y_tmp = data_y[:len(data_x)]
    data_x_tmp = data_x[0:len(data_y)]

    subplot.plot(data_x_tmp, data_y_tmp, 'g', linewidth=0.2)  # Hinzufügen des Graphen mit Werten der data-Arrays
    subplot.set_xlim(-scaler_x * 2, scaler_x * 2)  # Festlegen der Randwerte der x-Achse
    subplot.set_ylim(-scaler_y * 2, scaler_y * 2)  # Festlegen der Randwerte der y-Achse
    subplot.axhline(y=triggerValue, color='r')  # rote horizontale Linie für Triggerschwelle

    fig.canvas.draw_idle()


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

# text_label = Label(fenster, text=readLine(), bg="#FFF", fg="#000", font="Oswald, 18")

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
tri_str.set(str(triggerValue))

volt_spinbox = Spinbox(fenster, background="white", width=4, from_=1, to=5, increment=1, font="Oswald, 18", fg="#000",
                       bg="#FFF", command=volt_update_action, textvariable=volt_str)
time_spinbox = Spinbox(fenster, background="white", width=4, from_=0.1, to=10, increment=0.1, font="Oswald, 18",
                       fg="#000",
                       bg="#FFF", command=time_update_action, textvariable=time_str)
trigger_spinbox = Spinbox(fenster, background="white", width=4, from_=-10, to=10, increment=0.1, font="Oswald, 18",
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
# text_label.place(x=90, y=300)
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

exit_button.place(x=730, y=450)


def onClick(event):
    print(event.x, " ", event.y, " ", event.button)
    print(event.xdata, " ", event.ydata, " ", event.button)

def onDraw(event):
    print(event.xdata, " ", event.ydata, " ", event.button)


def onKey(event):
    print(event.xdata, " ", event.ydata, " ", event.key)


# Main
# Festlegen der Größe des Plots
global subplot
global fig
fig = Figure(dpi=100)
fig.set_figwidth(6.25)
fig.set_figheight(4)
subplot = fig.add_subplot(111)  # Erstellen des Graphen im Plot
canvas = FigureCanvasTkAgg(fig, master=fenster)
canvas.draw()
canvas.get_tk_widget().place(x=175, y=30)
fig.canvas.mpl_connect('button_press_event', onClick)
fig.canvas.mpl_connect('button_release_event', onClick)
#fig.canvas.mpl_connect('key_press_event', onKey)

makeFig()
fenster.mainloop()
#'resize_event', 'draw_event', 'key_press_event', 'key_release_event', 'button_press_event', 'button_release_event',
# 'scroll_event', 'motion_notify_event', 'pick_event', 'figure_enter_event', 'figure_leave_event', 'axes_enter_event', 'axes_leave_event', 'close_event'

# todo Trigger als Schiebebalken rechts/links neben fenster
# todo Offset für Voltage
# todo toggle buttons für welche flanke triggern

# todo Platine für optische Schönheit
