import tkinter
from tkinter import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
from tkinter import ttk

# Globale Variable
global scaler_x  # X-Achsen Skalierung
scaler_x = 0.5

global scaler_y  # Y-Achsen Skalierung
scaler_y = 3

global triggerValue  # Variable für Triggerschwelle
triggerValue = 2.0

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

# Button-Actions
def auto_trigger_action():  # todo
    fenster.quit()


def time_update_action():
    fenster.quit()

def volt_update_action():
    fenster.quit()

def trigger_update_action():
    fenster.quit()

def windowClose():
    fenster.quit()

def start_button_action():
    fenster.quit()

def stop_button_action():
    fenster.quit()

def reset_button_action():
    fenster.quit()

def trigger_button_action():
    fenster.quit()

def makeFig():
    global data_x
    global data_y
    global subplot
    global fig
    global tlast

    fig.delaxes(subplot)
    subplot = fig.add_subplot(111)
    subplot.plot(data_x, data_y, 'g', linewidth=0.2)  # Hinzufügen des Graphen mit Werten der data-Arrays
    subplot.plot([-1.5 * scaler_x, -1.5 * scaler_x], [-2 * scaler_y, 2 * scaler_y], 'g', linewidth=0.2)
    subplot.set_xlim(-scaler_x * 2, scaler_x * 2)  # Festlegen der Randwerte der x-Achse
    subplot.set_ylim(-scaler_y * 2, scaler_y * 2)  # Festlegen der Randwerte der y-Achse
    subplot.axhline(y=triggerValue, color='r')  # rote horizontale Linie für Triggerschwelle

    fig.canvas.draw_idle()


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
start_button = Button(fenster, text="Start", command=start_button_action, bg="green", fg="white", width="4")
stop_button = Button(fenster, text="Stop", command=stop_button_action, bg="red", fg="white", width="4")
reset_values_button = Button(fenster, text="Reset Values", command=reset_button_action, height="1", width="10")
reset_zoom_button = Button(fenster, text="Reset Zoom", command=windowClose, width="10")
reset_cursor_button = Button(fenster, text="Reset Cursor", command=windowClose, width="10")

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
trigger_scrollbar = Scrollbar(fenster, command=windowClose, width=25, orient=VERTICAL)
cursor1_scrollbar = Scrollbar(fenster, command=windowClose, width=25, orient=HORIZONTAL)
cursor2_scrollbar = Scrollbar(fenster, command=windowClose, width=25, orient=HORIZONTAL)

# Combobox
n = tkinter.StringVar()
trigger_style = ttk.Combobox(fenster, width = 6, textvariable = n, font="Oswald, 18")
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
global subplot
global fig
fig = Figure(dpi=100, facecolor='blue', figsize=(6, 3.25), tight_layout=True)
subplot = fig.add_subplot(111)  # Erstellen des Graphen im Plot
canvas = FigureCanvasTkAgg(fig, master=fenster)
canvas.draw()
canvas.get_tk_widget().place(x=170, y=0)

makeFig()
fenster.mainloop()

# Trigger als Schiebebalken rechts/links neben fenster, scrollrad weg
# todo Offset für Voltage
# toggle buttons für welche flanke triggern
# auto-trigger raus
# todo cursor und zoom mit finger
# todo reset für cursor, zoom
# todo anzeige für cursor x/y + dif zwischen cursor
# todo popup für Fehler
# todo Triggerschwelle nicht anzeigen bei Einstellung "None"

# todo Platine für optische Schönheit
