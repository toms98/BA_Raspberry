import tkinter
from tkinter import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
import threading
import time
from tkinter import ttk
# from matplotlib.backend_bases import key_press_handler
# from matplotlib import pyplot as plt

# global mode, design, scaler_x, scaler_y, trigger, event, samplePerSecond, checker, data_x, data_y, isRunning, thread
mode = "MAC"                # Betriebsmodus 0 = Mac, 1 = RPi
design = "NEU"              # GUI-Auswahl 0 = alt, 1 = neu
scaler_x = 0.5              # X-Achsen Skalierung
scaler_y = 3                # Y-Achsen Skalierung
trigger = 2.0               # Variable für Triggerschwelle
event = threading.Event()   # Event für Threading Prozess
samplePerSecond = 860       # Samples per Second des Microcontrollers
checker = False             # Boolean für Trigger (in)aktiv
data_x = []                 # Datenarray für X-Werte
data_y = []                 # Datenarray für Y-Werte
isRunning = False           # Boolean für Aufzeichnung (in)aktiv
fenster = 0                 # Fenster das bei Start geöffnet wird

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
    scaler_x = float(time_spinbox.get())
    if not isRunning:
        make_fig()


def volt_update_action():
    global scaler_y
    global isRunning
    scaler_y = float(volt_spinbox.get())
    if not isRunning:
        make_fig()


def trigger_update_action():
    global trigger
    trigger = float(trigger_spinbox.get())
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
    global trigger
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
    global thread # todo Lösung warum thread unterstrichen?
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


tlast = time.time()


def make_fig():
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


if design == "ALT":
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

    # Buttons
    exit_button = Button(fenster, text="Beenden", command=window_close, bg="#FFF", fg="#000", height="1", width="4")

    start_button = Button(fenster, text="Start", command=start_button_action, bg="white", fg="black", height="1",
                          width="4")
    stop_button = Button(fenster, text="Stop", command=stop_button_action, bg="white", fg="black", height="1",
                         width="4")
    reset_button = Button(fenster, text="Reset", command=reset_button_action, bg="white", fg="black", height="1",
                          width="4")

    # Spinboxes
    volt_str = StringVar(fenster)
    time_str = StringVar(fenster)
    tri_str = StringVar(fenster)
    volt_str.set(str(scaler_y))
    time_str.set(str(scaler_x))
    tri_str.set(str(trigger))

    volt_spinbox = Spinbox(fenster, background="white", width=4, from_=1, to=5, increment=1, font="Oswald, 18",
                           fg="black", bg="white", command=volt_update_action, textvariable=volt_str)
    time_spinbox = Spinbox(fenster, background="white", width=4, from_=0.1, to=10, increment=0.1, font="Oswald, 18",
                           fg="black",
                           bg="white", command=time_update_action, textvariable=time_str)
    trigger_spinbox = Spinbox(fenster, background="white", width=4, from_=-10, to=10, increment=0.1, font="Oswald, 18",
                              fg="black", bg="white", command=trigger_update_action, textvariable=tri_str)

    # Checkbox
    trigger_checkbox = Checkbutton(fenster, variable=checker, background="white", font="Oswald, 18", fg="white",
                                   bg="black", command=trigger_button_action)

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
    fig = Figure(dpi=100)
    fig.set_figwidth(6.25)
    fig.set_figheight(4)
    subplot = fig.add_subplot(111)  # Erstellen des Graphen im Plot
    canvas = FigureCanvasTkAgg(fig, master=fenster)
    canvas.draw()
    canvas.get_tk_widget().place(x=175, y=30)


if design == "NEU":
    # Fenster erstellen
    fenster = Tk()
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
    reset_zoom_button = Button(fenster, text="Reset Zoom", command=window_close, width="10")
    reset_cursor_button = Button(fenster, text="Reset Cursor", command=window_close, width="10")

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
    trigger_scrollbar = Scrollbar(fenster, command=window_close, width=25, orient=VERTICAL)
    cursor1_scrollbar = Scrollbar(fenster, command=window_close, width=25, orient=HORIZONTAL)
    cursor2_scrollbar = Scrollbar(fenster, command=window_close, width=25, orient=HORIZONTAL)

    # Combobox
    n = tkinter.StringVar()
    trigger_style = ttk.Combobox(fenster, width=6, textvariable=n, font="Oswald, 18")
    trigger_style['values'] = ('None', 'Rising', 'Falling', 'Both')
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
    frequency2_label.place(x=95, y=260)
    frequency3_label.place(x=125, y=260)

    period1_label.place(x=5, y=290)
    period2_label.place(x=95, y=290)
    period3_label.place(x=125, y=290)

    timedif1_label.place(x=5, y=320)
    timedif2_label.place(x=95, y=320)
    timedif3_label.place(x=125, y=320)

    voltdif1_label.place(x=5, y=350)
    voltdif2_label.place(x=95, y=350)
    voltdif3_label.place(x=125, y=350)

    start_button.place(x=5, y=380)
    stop_button.place(x=70, y=380)
    reset_values_button.place(x=135, y=380)
    reset_zoom_button.place(x=250, y=380)
    reset_cursor_button.place(x=365, y=380)

    trigger_scrollbar.place(x=770, y=0, height=325)
    cursor1_scrollbar.place(x=170, y=325, width=600)
    cursor2_scrollbar.place(x=170, y=350, width=600)

    # Main
    # Festlegen der Größe des Plots
    fig = Figure(dpi=100, facecolor='blue', figsize=(6, 3.25), tight_layout=True)
    subplot = fig.add_subplot(111)  # Erstellen des Graphen im Plot
    canvas = FigureCanvasTkAgg(fig, master=fenster)
    canvas.draw()
    canvas.get_tk_widget().place(x=170, y=0)

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
