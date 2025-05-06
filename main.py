# Much of this work is based on:
# https://github.com/chvvkumar/PiSQM/tree/main
# and
# https://www.mnassa.org.za/html/Oct2017/2017MNASSA..76..Oct..215.pdf
#
# I = 3.719 x 10^(-9-0.4*M)  W/m2s2
#
# 1 W/m2 = 1 W/10^4 cm2 = 10^-4 W/cm2 = 100 uW/cm2
#
# I = 3.719 x 10^(-7-0.4*M)  uW/cm2s2
#
# from datasheet: at gain = 400 and T = 100 ms, 264 counts / uW/cm2
# this conversion is done in tsl2591.calculate_light()
# 
# log (I) = log (3.719) - 7 - 0.4 M
#
# M = -16.07 - 2.5*log(C)

# Anduino SQM formula for TSL237 light-to-frequency-sensor from
# https://stargazerslounge.com/topic/366438-diy-sky-quality-meter/
# const float A = 19.0;
# Msqm = A - 2.5*log10(frequency); //Frequency to magnitudes/arcSecond2 formula

from machine import Pin, I2C
import tsl2591
import time
import math
import sys
import network
import usocket as socket
import secrets
import json

# Constants
SSIDS = secrets.SSIDS.split(',')
PASSWORDS = secrets.PASSWORDS.split(',')
I2CDATA = 16
I2CCLK = 17
LED = machine.Pin("LED", machine.Pin.OUT)
CONFIG = {"integration": tsl2591.INTEGRATIONTIME_100MS, "gain": tsl2591.GAIN_LOW, 'm0': -16.07, 'ga': 25.55}
INTEGRATION_TIME_ARRAY = (['100ms', '200ms', '300ms', '400ms', '500ms', '600ms'])
GAIN_ARRAY = (['Low', 'Med', 'High', 'Max'])
PORT = 10001
COMMANDS = (b'rxc  = display sensor + config\r'
            b'rx   = display sensor\r'
            b'show = display config\r'
            b'help = display commands\r'
            b'save = save config\r'
            b'exit = close connection\r'
            b'gain [arg] = display/set gain [low, med, high, max]\r'
            b'time [arg] = display/set time [100, 200, 300, 400, 500, 600]\r'
            b'm0 [arg]   = display/set m0 factor [defualt -16.07]\r'
            b'ga [arg]   = display/set glass attenuation factor [default 25.55]\r>> ')

def hex_to_dec(hex):
    if hex == 0x00:
        return 0
    elif hex == 0x10:
        return 1
    elif hex == 0x20:
        return 2
    elif hex == 0x30:
        return 3

def connect_TCP():
    try:
        flash_led(5, 1)
        wlan = network.WLAN(network.STA_IF)
        wlan.config(hostname='AstroBobert_SQM')
        wlan.active(True)
        available_networks = wlan.scan()
        indx = 0
        for ssid in SSIDS:
            found, tuple_found = search_tuple_array(available_networks, ssid.encode())
            if found:
                print(f"SSID: {ssid} found")
                SSID = tuple_found[0]
                PASSWORD = PASSWORDS[indx].encode()
            else:
                print(f"SSID: {ssid} not found")
            indx += 1
            print(indx)
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            flash_led(1, 0.5)
        print('Wifi Connected')
        ip_address = wlan.ifconfig()[0]
    
        addr = socket.getaddrinfo(ip_address, 10001)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        print('listening on', addr)
        LED.on()
        return s
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

def search_tuple_array(array, value):
    for tuple_item in array:
        if value in tuple_item:
            return True, tuple_item  # Return True and the tuple if found
    return False, None  # Return False and None if not found

def change_gain(value):
    global CONFIG
    if value == b'low':
        tsl.set_gain(tsl2591.GAIN_LOW)
    elif value == b'med':
        tsl.set_gain(tsl2591.GAIN_MED)
    elif value == b'high':
        tsl.set_gain(tsl2591.GAIN_HIGH)
    elif value == b'max':
        tsl.set_gain(tsl2591.GAIN_MAX)
    print(f'Gain is {GAIN_ARRAY[hex_to_dec(tsl.gain)]}')
    CONFIG['gain'] = tsl.gain
     
def change_time(value):
    global CONFIG
    if value == b'100':
        tsl.set_timing(tsl2591.INTEGRATIONTIME_100MS)
    elif value == b'200':
        tsl.set_timing(tsl2591.INTEGRATIONTIME_200MS)
    elif value == b'300':
        tsl.set_timing(tsl2591.INTEGRATIONTIME_300MS)
    elif value == b'400':
        tsl.set_timing(tsl2591.INTEGRATIONTIME_400MS)
    elif value == b'500':
        tsl.set_timing(tsl2591.INTEGRATIONTIME_500MS)
    elif value == b'600':
        tsl.set_timing(tsl2591.INTEGRATIONTIME_600MS)
    print(f'Integration Time is {INTEGRATION_TIME_ARRAY[tsl.integration_time]}')
    CONFIG['integration'] = tsl.integration_time

def get_mpsas():
    print("Starting measurement loop...")
    mpsas_str = ''
    try:
        sample = tsl.sample()
        print(sample)
        if (sample > 0):
            mpsas = CONFIG['m0'] + CONFIG['ga'] - 2.5 * math.log10(sample)  
            if mpsas < 16.0:
                mpsas = -16.0
            if mpsas > 22.8:
                mpsas = -22.8
        else:
            mpsas = -25.0
        # Format and publish messages
        mpsas_msg = f"{mpsas:.2f}"
        #print(mpsas_msg)
        for i in range(6 - len(mpsas_msg)):
            mpsas_str = mpsas_str + ' '
        mpsas_str = mpsas_str + mpsas_msg
        return (f'r,{mpsas_str}m,0000005915Hz,0000000000c,0000000.000s, 000.0C')
    except Exception as e:
        print(f"Error in measurement function: {e}")

def init_tsl2591():
    # Initialize the TSL2591 sensor
    sdaPIN=Pin(I2CDATA)
    sclPIN=Pin(I2CCLK)
    i2c_bus = 0
    i2c=I2C(i2c_bus, sda=sdaPIN, scl=sclPIN, freq=400000)
    try:
        tsl = tsl2591.Tsl2591(i2c)
        tsl.set_gain(CONFIG['gain'])
        tsl.set_timing(CONFIG['integration'])
    except Exception as e:
        print(f"Failed to initialize TSL2591 sensor: {e}")
        flash_led(1000, 0.3)
    return tsl

def save_config():
    with open("lib/config.json", "w") as f:
        json.dump(CONFIG, f)

def open_config():
    global CONFIG
    try:
        with open("lib/config.json") as f:
            CONFIG = json.load(f)
    except Exception as e:
        print("Error in Main loop:", e)

def show_config():
    client_sock.send(f'Time = {INTEGRATION_TIME_ARRAY[CONFIG['integration']]}\rGain = {GAIN_ARRAY[hex_to_dec(CONFIG['gain'])]}\rM0 = {CONFIG['m0']}\rGA = {CONFIG['ga']}')

def flash_led(cnt, pause):
    for i in range(cnt):
        LED.off()
        time.sleep(pause)
        LED.on()
        time.sleep(pause)

LED.on()
connection = connect_TCP()
open_config()
tsl = init_tsl2591()

try:
    while True:
        client_sock, addr = connection.accept()
        print('Client connected from:', addr)

        ## Uncomment for terminal communication and calibration. Comment out for APT. Otherwise APT will receive COMMANDS instead of mpsas data when it connects
        # client_sock.send(COMMANDS)

        try:
            while True:
                request = client_sock.recv(1024)
                # print(request)
                command = request.split(b' ')
                if not request:
                    break
                elif command[0] == b'\r\n':
                    client_sock.send('\r>> ')
                elif command[0] == b'rxc':
                    _mpsas = get_mpsas() + '\r\n'
                    _gain={GAIN_ARRAY[hex_to_dec(tsl.gain)]}
                    _time={INTEGRATION_TIME_ARRAY[tsl.integration_time]}
                    mpsas_data = f'{_mpsas}\rgain={_gain} time={_time}'
                    client_sock.send(mpsas_data.encode()) # Echo back to client
                elif command[0] == b'rx':
                    LED.off()
                    time.sleep(0.5)
                    _mpsas = get_mpsas()
                    print(_mpsas.encode())
                    client_sock.send(_mpsas.encode()) # Echo back to client
                    LED.on()
                elif command[0] == b'time':
                    if len(command) == 2:
                        change_time(command[1])
                    client_sock.send('time = ' + INTEGRATION_TIME_ARRAY[tsl.integration_time]) # Echo back to client
                elif command[0] == b'gain':
                    if len(command) == 2:
                        change_gain(command[1])
                    client_sock.send('gain = ' + GAIN_ARRAY[hex_to_dec(tsl.gain)]) # Echo back to client
                elif command[0] == b'm0':
                    if len(command) == 2:
                        CONFIG['m0'] = float(command[1])
                    client_sock.send(f'M0 factor = {CONFIG['m0']}') # Echo back to client
                elif command[0] == b'ga':
                    if len(command) == 2:
                        CONFIG['ga'] = float(command[1])
                    client_sock.send(f'GA (glass attenuation) = {CONFIG['ga']}') # Echo back to client
                elif command[0] == b'show':
                    show_config()
                elif command[0] == b'save':
                    save_config() 
                elif command[0] == b'help':
                    client_sock.send(COMMANDS)
                elif command[0] == b'exit':
                    client_sock.send(b'done\r')
                    time.sleep(0.5)
                    break
                else:
                    client_sock.send(f'syntax error {command[0]}')
        except Exception as e:
            print("Error in Main loop:", e)
        finally:
            client_sock.close()
            print("Client disconnected")
except KeyboardInterrupt:
    print("\nInterrupted by Ctrl+C. Exiting...")

