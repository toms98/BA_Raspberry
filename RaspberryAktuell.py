import tkinter
from tkinter import *

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
import threading
import time
from tkinter import ttk

# from matplotlib.backend_bases import key_press_handler
# from matplotlib import pyplot as plt

TOUCH_SCREEN_PERCENTAGE = 50

# global mode, scaler_x, scaler_y, trigger, event, samplePerSecond, data_x, data_y, isRunning, thread
mode = "MAC"  # Betriebsmodus 0 = Mac, 1 = RPi
scaler_x = 0.5  # X-Achsen Skalierung
scaler_y = 3  # Y-Achsen Skalierung
triggerValue = 2.0  # Variable für Triggerschwelle
curserOne = None
curserTwo = None
showFromTo = [-2 * scaler_x, 2 * scaler_x]
event = threading.Event()  # Event für Threading Prozess
samplePerSecond = 860  # Samples per Second des Microcontrollers
data_x = []  # Datenarray für X-Werte
data_y = []  # Datenarray für Y-Werte
data_x_eval = []  # Datenarray für X-Werte
data_y_eval = []  # Datenarray für Y-Werte
isRunning = False  # Boolean für Aufzeichnung (in)aktiv
thread = threading.Thread  # todo kommentar
fenster = Tk()  # Fenster das bei Start geöffnet wird
triggerSelect = tkinter.StringVar()
vorteilerSelect = tkinter.StringVar()

GAIN_TO_MAX = {
    2/3: 6.144,
    1: 4.096,
    2: 2.048,
    4: 1.024,
    8: 0.512,
    16: 0.256
}

GAIN = 2/3

if mode == "RPI":
    import Adafruit_ADS1x15
    import RPi.GPIO as GPIO

if mode == "RPI":
    adc = Adafruit_ADS1x15.ADS1115()

    CHANNEL = 0

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    adc.start_adc(channel=CHANNEL, gain=GAIN, data_rate=samplePerSecond)


def get_offset():
    if mode == "MAC":
        return 0
        # return 53333
        # return 26666
    else:
        return adc.read_adc(2, gain=GAIN)


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


textDaten = []
datei = open("./rng2.txt", 'r')
for l in datei.readlines():
    textDaten.append(float(l.strip()))
counterDaten = 0


def readline():
    global scaler_x
    global counterDaten
    y = 0
    if mode == "MAC":
        for i in range(10000):
            print(end="")
        y = textDaten[counterDaten]
        counterDaten += 1
        if counterDaten == len(textDaten):
            counterDaten = 0
    if mode == "RPI":
        y = adc.get_last_result()
    x = time.time()
    return x, y


def main_thread():
    global isRunning
    global data_x
    global data_y

    data_old = None
    is_triggered = False

    time_update_action()

    offset = get_offset()

    counter = 0
    prescaler = 1
    if triggerSelect.get() == "1/4":
        prescaler = 0.25
    elif triggerSelect.get() == "1/2":
        prescaler = 0.5

    trigger_absolute = triggerValue * prescaler * 65535 / GAIN_TO_MAX[GAIN] + offset
    print("trigger=", triggerValue, "  absolute=", trigger_absolute)
    do_trigger = 0
    if triggerSelect.get() == "Falling":
        do_trigger = 1
    elif triggerSelect.get() == "Rising":
        do_trigger = 2
    elif triggerSelect.get() == "Both":
        do_trigger = 3

    x, y = readline()
    data_x.append(x)
    data_y.append(y)

    display_full_time = x + 4 * scaler_x
    trigger_after_time = x + 0.5 * scaler_x
    triggered_at_time = None

    while True:
        if event.is_set():
            event.clear()
            break

        x, y = readline()
        data_x.append(x)
        data_y.append(y)
        # Trigger
        if do_trigger != 0:
            if is_triggered:
                if x > display_full_time:
                    make_fig(triggered_at_time=triggered_at_time)
                    break
            else:
                if data_old is None:
                    data_old = y
                elif (((y >= trigger_absolute >= data_old) and (do_trigger == 2 or do_trigger == 3))\
                        or ((y <= trigger_absolute <= data_old) and (do_trigger == 1 or do_trigger == 3)))\
                        and (x > trigger_after_time):
                    data_old = None
                    triggered_at_time = x
                    is_triggered = True
                else:
                    data_old = y

        # nicht Trigger
        else:
            if x > display_full_time:
                make_fig()
                data_x = []
                data_y = []
                x, y = readline()
                data_x.append(x)
                data_y.append(y)
                display_full_time = x + 4 * scaler_x

    isRunning = False


def start_button_action():
    global event
    global isRunning
    global thread
    if isRunning:
        return
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
    # make_fig()
    make_fig_clear()


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


# noinspection PyUnresolvedReferences
def make_fig(triggered_at_time=None):
    global subplot
    global tlast
    global data_x
    global data_y
    global data_x_eval
    global data_y_eval

    print("zeit: ", time.time() - tlast)
    tlast = time.time()
    print("punkte: ", len(data_x), " freq: ", len(data_x) / (4 * scaler_x))

    if isRunning:
        if triggered_at_time is None:
            shift = data_x[0] + 2 * scaler_x
            data_x_eval = [i - shift for i in data_x]
        else:
            shift = triggered_at_time + 1.5 * scaler_x
            data_x_eval = [i - shift for i in data_x]

        offset = get_offset()
        prescaler = 1
        if vorteilerSelect.get() == "1/4":
            prescaler = 0.25
        elif vorteilerSelect.get() == "1/2":
            prescaler = 0.5
        mult = GAIN_TO_MAX[GAIN] / (65535 * prescaler)
        data_y_eval = [(i - offset) * mult for i in data_y]

    fig.delaxes(subplot)
    subplot = fig.add_subplot(111)
    subplot.plot(data_x_eval, data_y_eval, 'g', linewidth=0.2)  # Hinzufügen des Graphen mit Werten der data-Arrays
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
        voltage1 = 0
        voltage2 = 0
        for i in range(len(data_x_eval) - 1):
            if data_x_eval[i] < curserOne < data_x_eval[i + 1]:
                voltage1 = (data_y_eval[i] + data_y_eval[i + 1]) / 2
        for i in range(len(data_x_eval) - 1):
            if data_x_eval[i] < curserTwo < data_x_eval[i + 1]:
                voltage2 = (data_y_eval[i] + data_y_eval[i + 1]) / 2
        voltdif2_label.config(text=str(round((voltage2 - voltage1) * 1000, 2)))
        print("cursor1: x=", curserOne, " y=", voltage1)
        print("cursor2: x=", curserTwo, " y=", voltage2)
    else:
        timedif2_label.config(text="0.0")
    fig.canvas.draw_idle()


# noinspection PyUnresolvedReferences
def make_fig_clear():
    global subplot

    fig.delaxes(subplot)
    subplot = fig.add_subplot(111)
    # subplot.plot([], data_y, 'g', linewidth=0.2)  # Hinzufügen des Graphen mit Werten der data-Arrays
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


# noinspection PyGlobalUndefined
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
voltdif3_label = Label(fenster, text="mV", bg="white", fg="black", font="Oswald, 12")

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

volt_spinbox = Spinbox(fenster, width=4, from_=1, to=20, increment=1, font="Oswald, 18", fg="black",
                       bg="white", command=volt_update_action, textvariable=volt_str)
time_spinbox = Spinbox(fenster, width=4, from_=0.1, to=10, increment=0.1, font="Oswald, 18", fg="black",
                       bg="white", command=time_update_action, textvariable=time_str)

# Combobox
trigger_style = ttk.Combobox(fenster, width=6, textvariable=triggerSelect, font="Oswald, 18",
                             values=('None', 'Rising', 'Falling', 'Both'), state="readonly",
                             xscrollcommand=change_trigger_style)

trigger_style.place(x=5, y=170)
trigger_style.current(0)

vorteiler = ttk.Combobox(fenster, width=6, textvariable=vorteilerSelect, font="Oswald, 18",
                            values=('None', '1/2', '1/4'), state="readonly")
vorteiler.current(0)

vorteiler.place(x=500, y=380)

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

# Main
# Festlegen der Größe des Plots
fig = Figure(dpi=100, facecolor='blue', figsize=(6.3, 3.8), tight_layout=True)
subplot = fig.add_subplot(111)  # Erstellen des Graphen im Plot
canvas = FigureCanvasTkAgg(fig, master=fenster)
canvas.draw()
canvas.get_tk_widget().place(x=170, y=0)
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('button_release_event', on_release)

make_fig()
fenster.mainloop()

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

# 25.6
# todo Readline nur Rohdaten speichern
# todo Umrechnung bei Anzeige
# todo Einsteller für Vorteiler