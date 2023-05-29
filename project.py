from gpiozero import Buzzer
import RPi.GPIO as GPIO
import Adafruit_DHT
from tkinter import Tk, Label, Button, DISABLED, NORMAL, Entry
import time
from time import sleep

# Set up the buzzer 
buzzer = Buzzer(17)
def buzzer_buzz():
    start_time = time.time()
    end_time = start_time + 5
    while time.time() < end_time:
        buzzer.on()
        sleep(1)
        buzzer.off()
        sleep(1)
    buzzer.off()

GPIO_PIN = 27
GPIO.setmode(GPIO.BCM)  # Set pin numbering mode to BCM
GPIO.setup(GPIO_PIN, GPIO.IN)

alarm_triggered = False
alarm_acknowledged = False
last_alarm_time = 0
min_temperature = None
max_temperature = None
consecutive_out_of_range = 0

def read_sensor_data():
    try:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, GPIO_PIN)
        return temperature
    except Exception as e:
        print("Error reading data:", str(e))
        return None

def toggle_system():
    global system_enabled
    system_enabled = not system_enabled
    if system_enabled:
        button.config(text="Turn Off")
        status_label.config(text="System Status: ON")
        off_button.config(state=DISABLED)
        on_button.config(state=DISABLED)
        min_entry.config(state=DISABLED)
        max_entry.config(state=DISABLED)
        read_min_max_temperatures()
        update_temperature()
    else:
        button.config(text="Turn On")
        status_label.config(text="System Status: OFF")
        temperature_label.config(text="")
        hide_alarm()
        off_button.config(state=DISABLED)
        on_button.config(state=DISABLED)
        min_entry.config(state=NORMAL)
        max_entry.config(state=NORMAL)

def read_min_max_temperatures():
    global min_temperature, max_temperature
    min_temperature = int(min_entry.get())
    max_temperature = int(max_entry.get())

def update_temperature():
    global alarm_triggered, alarm_acknowledged, last_alarm_time
    
    if system_enabled:
        temperature = read_sensor_data()
        if temperature is not None:
            temperature_label.config(text="Temperature: {}°C".format(temperature))
            check_temperature(temperature)
            root.after(2000, update_temperature)  # Update every 2 seconds
    else:
        hide_alarm()
    
    # Reset the alarm after 2 minutes
    current_time = time.time()
    if current_time - last_alarm_time >= 120:
        alarm_triggered = False
        alarm_acknowledged = False

def check_temperature(temperature):
    global heater_acknowledged, alarm_triggered, alarm_acknowledged, last_alarm_time

    if temperature > max_temperature and not heater_acknowledged:
        if not alarm_triggered:
            show_alarm("TURN HEATER OFF")
            off_button.config(state=NORMAL)
            on_button.config(state=DISABLED)
            alarm_triggered = True
            last_alarm_time = time.time()
            buzzer_buzz()  # Activate the buzzer when alarm is triggered
        elif time.time() - last_alarm_time >= 120:
            alarm_triggered = True
            last_alarm_time = time.time()
            buzzer_buzz()  # Activate the buzzer when alarm is triggered
    elif temperature < min_temperature and not heater_acknowledged:
        if not alarm_triggered:
            show_alarm("TURN HEATER ON")
            off_button.config(state=DISABLED)
            on_button.config(state=NORMAL)
            alarm_triggered = True
            last_alarm_time = time.time()
            buzzer_buzz()  # Activate the buzzer when alarm is triggered
        elif time.time() - last_alarm_time >= 120:
            alarm_triggered = True
            last_alarm_time = time.time()
            buzzer_buzz()  # Activate the buzzer when alarm is triggered
    else:
        if temperature > min_temperature:
            heater_acknowledged = False
        hide_alarm()
        off_button.config(state=DISABLED)
        on_button.config(state=DISABLED)
        
    # Check consecutive out-of-range readings
    # This ensures the alarm doesnt go off based on one bad reading
    if alarm_triggered and temperature > max_temperature or temperature < min_temperature:
        consecutive_out_of_range += 1
        if consecutive_out_of_range >= 2:
            buzzer_buzz()  # Activate the buzzer after two consecutive out-of-range readings
    else:
        consecutive_out_of_range = 0

        
# This function contains the main logic of the program
# Checks the temperature with min/max temps
# Implements the consecutive checks to ensure temperature readings are accurate before triggering alarm
def check_temperature(temperature):
    global heater_acknowledged, alarm_triggered, alarm_acknowledged, last_alarm_time, consecutive_out_of_range

    if temperature > max_temperature and not heater_acknowledged:
        if not alarm_triggered:
            consecutive_out_of_range += 1
            if consecutive_out_of_range >= 2:
                show_alarm("TURN HEATER OFF")
                off_button.config(state=NORMAL)
                on_button.config(state=DISABLED)
                alarm_triggered = True
                last_alarm_time = time.time()
                buzzer_buzz()  # Activate the buzzer when alarm is triggered
        elif time.time() - last_alarm_time >= 120:
            consecutive_out_of_range += 1
            if consecutive_out_of_range >= 2:
                alarm_triggered = True
                last_alarm_time = time.time()
                buzzer_buzz()  # Activate the buzzer when alarm is triggered
    elif temperature < min_temperature and not heater_acknowledged:
        if not alarm_triggered:
            consecutive_out_of_range += 1
            if consecutive_out_of_range >= 2:
                show_alarm("TURN HEATER ON")
                off_button.config(state=DISABLED)
                on_button.config(state=NORMAL)
                alarm_triggered = True
                last_alarm_time = time.time()
                buzzer_buzz()  # Activate the buzzer when alarm is triggered
        elif time.time() - last_alarm_time >= 120:
            consecutive_out_of_range += 1
            if consecutive_out_of_range >= 2:
                alarm_triggered = True
                last_alarm_time = time.time()
                buzzer_buzz()  # Activate the buzzer when alarm is triggered
    else:
        if temperature > min_temperature:
            heater_acknowledged = False
        hide_alarm()
        off_button.config(state=DISABLED)
        on_button.config(state=DISABLED)
        consecutive_out_of_range = 0  # Reset the consecutive out-of-range counter

def show_alarm(message):
    alarm_label.config(text=message)
    alarm_label.pack()
    off_button.config(state=DISABLED)
    on_button.config(state=DISABLED)

def hide_alarm():
    alarm_label.pack_forget()
    off_button.config(state=DISABLED)
    on_button.config(state=DISABLED)

def acknowledge_off():
    global heater_acknowledged
    heater_acknowledged = True
    hide_alarm()

def acknowledge_on():
    global heater_acknowledged
    heater_acknowledged = True
    hide_alarm()

root = Tk()
root.title("Temperature Control System")  # Set the title of the window
root.geometry("400x400")    # Set the size of the window

status_label = Label(root, text="System Status: OFF")
temperature_label = Label(root, text="")
alarm_label = Label(root, text="", fg="red", font=("Arial", 24, "bold"))

button = Button(root, text="Turn On", command=toggle_system)
off_button = Button(root, text="Heater is off", state=DISABLED, command=acknowledge_off)
on_button = Button(root, text="Heater is on", state=DISABLED, command=acknowledge_on)

min_label = Label(root, text="Minimum Temperature:")
min_entry = Entry(root)

max_label = Label(root, text="Maximum Temperature:")
max_entry = Entry(root)

status_label.pack()
temperature_label.pack()
min_label.pack()
min_entry.pack()
max_label.pack()
max_entry.pack()
button.pack()
off_button.pack()
on_button.pack()

system_enabled = False  # The system starts off by default
heater_acknowledged = False # Heater is not acknowledged until the user pressses button

root.after(0, update_temperature)

root.mainloop()
