import tkinter
from tkinter import *

import matplotlib
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
import threading
import time
from tkinter import ttk

# from matplotlib.backend_bases import key_press_handler
# from matplotlib import pyplot as plt

TOUCH_SCREEN_PERCENTAGE = 50

# global mode, design, scaler_x, scaler_y, trigger, event, samplePerSecond, checker, data_x, data_y, isRunning, thread
mode = "MAC"  # Betriebsmodus 0 = Mac, 1 = RPi
design = "NEU"  # GUI-Auswahl 0 = alt, 1 = neu
scaler_x = 0.5  # X-Achsen Skalierung
scaler_y = 3  # Y-Achsen Skalierung
triggerValue = 2.0  # Variable für Triggerschwelle
curserOne = None
curserTwo = None
showFromTo = [-2 * scaler_x, 2 * scaler_x]
event = threading.Event()  # Event für Threading Prozess
samplePerSecond = 860  # Samples per Second des Microcontrollers
data_x = [-1, 1]  # Datenarray für X-Werte
data_y = [-6, 6]  # Datenarray für Y-Werte
isRunning = False  # Boolean für Aufzeichnung (in)aktiv
thread = threading.Thread  # todo kommentar
fenster = Tk()  # Fenster das bei Start geöffnet wird
checker = BooleanVar()  # Boolean für Trigger (in)aktiv
triggerSelect = tkinter.StringVar()

if mode == "RPI":
    import Adafruit_ADS1x15
    import RPi.GPIO as GPIO

if mode == "RPI":
    adc = Adafruit_ADS1x15.ADS1115()

    CHANNEL = 0
    GAIN = 1

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    adc.start_adc(channel=CHANNEL, gain=GAIN, data_rate=samplePerSecond)


# Button-Actions
def auto_trigger_action():  # todo
    fenster.quit()


def time_update_action():
    global scaler_x
    global data_x
    global data_y
    global isRunning
    global showFromTo
    scaler_x = float(time_spinbox.get())
    showFromTo = [-2 * scaler_x, 2 * scaler_x]
    if not isRunning:
        make_fig()


def volt_update_action():
    global scaler_y
    global isRunning
    scaler_y = float(volt_spinbox.get())
    if not isRunning:
        make_fig()


def window_close():
    global event
    event.set()
    fenster.destroy()


# global timeRef
timeRef = -1.0


def readline():
    global scaler_x
    global timeRef
    y = 0
    if mode == "MAC":
        y = 0
    if mode == "RPI":
        y = float(adc.get_last_result()) / 8000
    t = time.time()
    if timeRef < 0:
        timeRef = t
    x = t - timeRef - 2 * scaler_x
    return x, y, t


def main_thread():
    # aktualisieren des Labels bei Knopfdruck
    global triggerValue
    global checker
    global scaler_x
    global isRunning
    global timeRef
    global data_x
    global data_y

    data_old = None
    is_triggered = False
    # points_together = 100

    time_update_action()

    counter = 0

    while True:
        if event.is_set():
            event.clear()
            break

        x, y, t = readline()
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
                    make_fig()
                    data_x = []
                    data_y = []
                    timeRef = -1.
                    break
            else:
                if data_old is None:
                    data_old = y
                elif (y >= triggerValue >= data_old) or (y <= triggerValue <= data_old):
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
                        make_fig()
                        counter = 0
                    timeRef = t
                    # print(data_x)
                    # print(data_y)
                    print(len(data_x))
                    length = round(scaler_x * samplePerSecond)
                    data_x = data_x[-length:]
                    shift = - scaler_x * 2 - x
                    data_x = [i + shift for i in data_x]
                    data_y = data_y[-length:]

        # nicht Trigger
        else:
            if x > 2 * scaler_x:
                make_fig()
                data_x = []
                data_y = []
                timeRef = -1.0

    isRunning = False


def start_button_action():
    global event
    global isRunning
    global thread  # todo Lösung warum thread unterstrichen?
    global checker
    if isRunning:
        return
    if checker:
        reset_button_action()
    event.clear()
    isRunning = True
    thread = threading.Thread(target=main_thread)
    thread.do_run = True
    thread.start()


def stop_button_action():
    # Stoppen des Auslese-Threads
    global event
    global isRunning
    event.set()
    isRunning = False


def reset_button_action():
    # Zurücksetzen aller Variablen und updaten des Graphen
    global data_x
    global data_y
    global fig
    global triggerValue
    global subplot
    stop_button_action()
    data_x.clear()
    data_y.clear()
    make_fig()


def reset_zoom_callback():
    global showFromTo
    showFromTo = [-2 * scaler_x, 2 * scaler_x]
    make_fig()


def reset_cursor_callback():
    global curserOne
    global curserTwo
    curserOne = None
    curserTwo = None
    make_fig()


tlast = time.time()


def make_fig():
    global subplot
    global tlast
    print("c1=", curserOne, "  c2=", curserTwo)

    # print("zeit: ", time.time() - tlast)
    # tlast = time.time()
    # print("punkte: ", len(data_x), " freq: ", len(data_x) / (4 * scaler_x))

    fig.delaxes(subplot)
    subplot = fig.add_subplot(111)
    subplot.plot(data_x, data_y, 'g', linewidth=0.2)  # Hinzufügen des Graphen mit Werten der data-Arrays
    subplot.set_xlim(showFromTo[0], showFromTo[1])  # Festlegen der Randwerte der x-Achse
    subplot.set_ylim(-scaler_y * 2, scaler_y * 2)  # Festlegen der Randwerte der y-Achse
    if triggerSelect.get() != 'None':
        subplot.axhline(y=triggerValue, color='r')  # rote horizontale Linie für Triggerschwelle
    if curserOne is not None:
        subplot.axvline(x=curserOne, color='b')
    if curserTwo is not None:
        subplot.axvline(x=curserTwo, color='b')
    if curserOne is not None and curserTwo is not None:
        timedif2_label.config(text=str(round(curserTwo - curserOne, 2)))
    else:
        timedif2_label.config(text="0.0")
    fig.canvas.draw_idle()


def change_trigger_style(x, y):
    make_fig()


def on_click(e):
    global eOld
    # print("x:", e.x, " y:", e.y, " ", e.button)
    # print("xDat:", e.xdata, " yDat:", e.ydata, " ", e.button)
    eOld = e


def on_release(e):
    # print("x:", e.x, " y:", e.y, " ", e.button)
    # print("xDat:", e.xdata, " yDat:", e.ydata, " ", e.button)
    global curserOne
    global curserTwo
    global triggerValue
    global showFromTo
    if isRunning:
        return

    # move curser one
    if curserOne is None and eOld.xdata is None and e.xdata is not None:
        curserOne = e.xdata
        make_fig()
        return
    if curserOne is not None and e.xdata is not None and eOld.xdata is not None and (
            curserOne - 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE) < eOld.xdata < (
            curserOne + 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE):
        curserOne = e.xdata
        make_fig()
        return
    if curserOne is not None and e.xdata is None and eOld.xdata is not None and (
            curserOne - 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE) < eOld.xdata < (
            curserOne + 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE):
        curserOne = None
        make_fig()
        return

    # move curser two
    if curserTwo is None and eOld.xdata is None and e.xdata is not None:
        curserTwo = e.xdata
        make_fig()
        return
    if curserTwo is not None and e.xdata is not None and eOld.xdata is not None and (
            curserTwo - 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE) < eOld.xdata < (
            curserTwo + 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE):
        curserTwo = e.xdata
        make_fig()
        return
    if curserTwo is not None and e.xdata is None and eOld.xdata is not None and (
            curserTwo - 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE) < eOld.xdata < (
            curserTwo + 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE):
        curserTwo = None
        make_fig()
        return

    # move trigger
    if triggerSelect.get() != 'None' and e.ydata is not None and eOld.ydata is not None and (
            triggerValue - 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE) < eOld.ydata < (
            triggerValue + 2 * showFromTo[1] / TOUCH_SCREEN_PERCENTAGE):
        triggerValue = e.ydata
        make_fig()
        return

    # zoom
    if e.xdata is not None and eOld.xdata is not None:
        if eOld.xdata < e.xdata:
            showFromTo = [eOld.xdata, e.xdata]
        else:
            showFromTo = [e.xdata, eOld.xdata]
        make_fig()
        return


# if design == "NEU":
# Fenster erstellen
# fenster = Tk()
fenster.title("Oszilloskop")  # Name des Fensters
fenster.configure(background="white")

# Labels
voltage_label = Label(fenster, text="Volts", bg="#FFF", fg="#000", font="Oswald, 18")
time_label = Label(fenster, text="Time", bg="#FFF", fg="#000", font="Oswald, 18")

triggerstyle_label = Label(fenster, text="Triggerstyle:", bg="#FFF", fg="#000", font="Oswald, 16")
trigger_value_label = Label(fenster, text="0.0", bg="blue", fg="#000", font="Oswald, 18")
trigger_volt_label = Label(fenster, text="V", bg="red", fg="#000", font="Oswald, 18", width=2)

frequency1_label = Label(fenster, text="Frequency:", bg="#FFF", fg="#000", font="Oswald, 12")
frequency2_label = Label(fenster, text="0.0", bg="red", fg="black", font="Oswald, 12")
frequency3_label = Label(fenster, text="f/Hz", bg="#FFF", fg="#000", font="Oswald, 12")

period1_label = Label(fenster, text="Period:", bg="white", fg="black", font="Oswald, 12")
period2_label = Label(fenster, text="0.0", bg="red", fg="black", font="Oswald, 12")
period3_label = Label(fenster, text="T/ms", bg="white", fg="black", font="Oswald, 12")

timedif1_label = Label(fenster, text="Time Diff.:", bg="white", fg="black", font="Oswald, 12")
timedif2_label = Label(fenster, text="0.0", bg="red", fg="black", font="Oswald, 12")
timedif3_label = Label(fenster, text="s", bg="white", fg="black", font="Oswald, 12")

voltdif1_label = Label(fenster, text="Volt Diff.:", bg="white", fg="black", font="Oswald, 12")
voltdif2_label = Label(fenster, text="0.0", bg="red", fg="black", font="Oswald, 12")
voltdif3_label = Label(fenster, text="mV:", bg="white", fg="black", font="Oswald, 12")

# Buttons
start_button = Button(fenster, text="Start", command=start_button_action, bg="white", fg="black", width="4")
stop_button = Button(fenster, text="Stop", command=stop_button_action, bg="white", fg="black", width="4")
reset_values_button = Button(fenster, text="Reset Values", command=reset_button_action, height="1", width="10")
reset_zoom_button = Button(fenster, text="Reset Zoom", command=reset_zoom_callback, width="10")
reset_cursor_button = Button(fenster, text="Reset Cursor", command=reset_cursor_callback, width="10")

# Spinboxes
volt_str = StringVar(fenster)
time_str = StringVar(fenster)
volt_str.set(str(scaler_y))
time_str.set(str(scaler_x))

volt_spinbox = Spinbox(fenster, width=4, from_=1, to=5, increment=1, font="Oswald, 18", fg="black",
                       bg="white", command=volt_update_action, textvariable=volt_str)
time_spinbox = Spinbox(fenster, width=4, from_=0.1, to=10, increment=0.1, font="Oswald, 18", fg="black",
                       bg="white", command=time_update_action, textvariable=time_str)

# Scrollbar
# trigger_scrollbar = Scrollbar(fenster, command=trigger_scroll_callback, width=25, orient=VERTICAL)
# cursor1_scrollbar = Scrollbar(fenster, command=curser_one_callback, width=25, orient=HORIZONTAL)
# cursor2_scrollbar = Scrollbar(fenster, command=curser_two_callback, width=25, orient=HORIZONTAL)

# Combobox
trigger_style = ttk.Combobox(fenster, width=6, textvariable=triggerSelect, font="Oswald, 18",
                             values=('None', 'Rising', 'Falling', 'Both'), state="readonly",
                             xscrollcommand=change_trigger_style)
# trigger_style['values'] = ('None', 'Rising', 'Falling', 'Both')
trigger_style.place(x=5, y=170)
trigger_style.current(0)

# Window
fenster.geometry("800x410")

# Orientation
volt_spinbox.place(x=5, y=20, height=50)
voltage_label.place(x=90, y=20, height=50)

time_spinbox.place(x=5, y=80, height=50)
time_label.place(x=90, y=80, height=50)

triggerstyle_label.place(x=5, y=140)
trigger_value_label.place(x=5, y=210)
trigger_volt_label.place(x=50, y=210)

frequency1_label.place(x=5, y=260)
frequency2_label.place(x=85, y=260)
frequency3_label.place(x=125, y=260)

period1_label.place(x=5, y=290)
period2_label.place(x=85, y=290)
period3_label.place(x=125, y=290)

timedif1_label.place(x=5, y=320)
timedif2_label.place(x=85, y=320)
timedif3_label.place(x=125, y=320)

voltdif1_label.place(x=5, y=350)
voltdif2_label.place(x=85, y=350)
voltdif3_label.place(x=125, y=350)

start_button.place(x=5, y=380)
stop_button.place(x=70, y=380)
reset_values_button.place(x=135, y=380)
reset_zoom_button.place(x=250, y=380)
reset_cursor_button.place(x=365, y=380)

# trigger_scrollbar.place(x=770, y=0, height=325)
# cursor1_scrollbar.place(x=170, y=325, width=600)
# cursor2_scrollbar.place(x=170, y=350, width=600)

# Main
# Festlegen der Größe des Plots
fig = Figure(dpi=100, facecolor='blue', figsize=(6, 3.25), tight_layout=True)
subplot = fig.add_subplot(111)  # Erstellen des Graphen im Plot
canvas = FigureCanvasTkAgg(fig, master=fenster)
canvas.draw()
canvas.get_tk_widget().place(x=170, y=0)
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('button_release_event', on_release)

make_fig()
fenster.mainloop()

# Trigger als Schiebebalken rechts/links neben fenster, Scrollrad weg
# Offset für Voltage
# toggle buttons für welche flanke triggern
# auto-trigger raus
# todo cursor und zoom mit finger
# todo reset für cursor, zoom
# anzeige für cursor x/y + dif zwischen cursor
# Platine

# 13.6
# Spannungsversorgung für ADC ändern
# Trigger aktiv und Signal liegt an. Start drücken Signal vor Trigger nicht aufgezeichnet
# todo Achsenskallierung y-Achse fixen
# todo https://www.best-microcontroller-projects.com/ads1115.html
# todo https://www.mikrocontroller.net/topic/439100
# Überlegung Offset auf Eingangsspannung legen, damit keine neg. Versorgung notwendig wird

# todo falstad.com/circuit Simulation
# todo easyeda.com/de Schaltplan + Layout

# 20.6
# todo neues Design mit Funktionen belegen
