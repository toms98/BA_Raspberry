from tkinter import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
import numpy as np
from drawnow import *
import threading
import time

import Adafruit_ADS1x15
import RPi.GPIO as GPIO


# Globale Variable
global scaler_x  # X-Achsen Skalierung
scaler_x = 0.5

global scaler_y  # Y-Achsen Skalierung
scaler_y = 3

global trigger  # Variable für Triggerschwelle
trigger = 2.0

global event  # Event für Threading Prozess
event = threading.Event()

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

adc = Adafruit_ADS1x15.ADS1115()

CHNL = 0
GAIN = 1
# pwmpin = 32

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# GPIO.setup(pwmpin, GPIO.OUT)
# pi_pwm = GPIO.PWM(pwmpin, 1)
# pi_pwm.start(0)

adc.start_adc(channel=CHNL, gain=GAIN, data_rate=samplePerSecond)


# Button-Actions
def auto_trigger_action():  # todo
    fenster.quit()


def time_update_action():
    global scaler_x
    global data_x
    global data_y
    global isRunning
    scaler_x = float(time_spinbox.get())
    if not isRunning:
        makeFig()


def volt_update_action():
    global scaler_y
    global isRunning
    scaler_y = float(volt_spinbox.get())
    if not isRunning:
        makeFig()


def trigger_update_action():
    global trigger
    trigger = float(trigger_spinbox.get())
    if not isRunning:
        makeFig()


def windowClose():
    global event
    event.set()
    fenster.destroy()


global timeRef
timeRef = -1.0


def readLine():
    global scaler_x
    global timeRef
    y = float(adc.get_last_result()) / 8000
    t = time.time()
    if timeRef < 0:
        timeRef = t
    x = t - timeRef - 2 * scaler_x
    return x, y, t


def mainThread():
    # aktualisieren des Labels bei Knopfdruck
    global trigger
    global checker
    global scaler_x
    global isRunning
    global timeRef
    data_old = None
    is_triggered = False

    # todo
    global data_x
    global data_y

    POINTS_TOGETHER = 100

    time_update_action()

    counter = 0

    while (True):
        if event.is_set():
            event.clear()
            break

        x, y, t = readLine()
        data_x.append(x)
        data_y.append(y)
        # Trigger
        if checker:
            if is_triggered:
                if x > 2 * scaler_x:
                    while True:
                        if data_x[0] < -scaler_x * 2:
                            data_x.remove(data_x[0])
                            data_y.remove(data_y[0])
                            continue
                        break
                    makeFig()
                    data_x = []
                    data_y = []
                    timeRef = -1.
                    break
            else:
                if data_old is None:
                    data_old = y
                elif (y >= trigger >= data_old) or (y <= trigger <= data_old):
                    data_old = None
                    is_triggered = True
                    shift = scaler_x * 1.5 + x
                    timeRef += shift
                    data_x = [i - shift for i in data_x]
                else:
                    data_old = y
                if x > - scaler_x * 1.5:
                    counter += 1
                    if counter * scaler_x * 0.5 >= 0.5:
                        makeFig()
                        counter = 0
                    timeRef = t
                    # print(data_x)
                    # print(data_y)
                    print(len(data_x))
                    l = round(scaler_x * samplePerSecond)
                    data_x = data_x[-l:]
                    shift = - scaler_x * 2 - x
                    data_x = [i + shift for i in data_x]
                    data_y = data_y[-l:]



        # nicht Trigger
        else:
            if x > 2 * scaler_x:
                makeFig()
                data_x = []
                data_y = []
                timeRef = -1.0

    isRunning = False


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
    event.set()
    isRunning = False


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
    subplot.axhline(y=trigger, color='r')  # rote horizontale Linie für Triggerschwelle
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
    global tlast

    print("zeit: ", time.time() - tlast)
    tlast = time.time()
    print("punkte: ", len(data_x), " freq: ", len(data_x) / (4 * scaler_x))

    fig.delaxes(subplot)
    subplot = fig.add_subplot(111)
    subplot.plot(data_x, data_y, 'g', linewidth=0.2)  # Hinzufügen des Graphen mit Werten der data-Arrays
    subplot.plot([-1.5 * scaler_x, -1.5 * scaler_x], [-2 * scaler_y, 2 * scaler_y], 'g', linewidth=0.2)
    subplot.set_xlim(-scaler_x * 2, scaler_x * 2)  # Festlegen der Randwerte der x-Achse
    subplot.set_ylim(-scaler_y * 2, scaler_y * 2)  # Festlegen der Randwerte der y-Achse
    subplot.axhline(y=trigger, color='r')  # rote horizontale Linie für Triggerschwelle

    fig.canvas.draw_idle()


# Fenster erstellen
fenster = Tk()
fenster.title("Oszilloskop")  # Name des Fensters
fenster.configure(background="white")

# plt.rcParams['toolbar'] = 'None' #anscheinend unnötig bei canvas

# Labels
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

trigger_checkbox.place(x=90, y=260)

cur_fre_label.place(x=35, y=390)
cur_per_label.place(x=35, y=420)
cur_vol_label.place(x=35, y=450)

frequency_label.place(x=65, y=390)
period_label.place(x=65, y=420)
cursor_label.place(x=65, y=450)

trigger_button_label.place(x=120, y=270)

exit_button.place(x=730, y=450)

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

makeFig()
fenster.mainloop()

# todo Trigger als Schiebebalken rechts/links neben fenster, scrollrad weg
# todo Offset für Voltage
# todo toggle buttons für welche flanke triggern
# todo auto-trigger raus
# cursor und zoom mit finger
# reset für cursor, zoom
# anzeige für cursor x/y + dif zwischen cursor

# todo Platine für optische Schönheit
