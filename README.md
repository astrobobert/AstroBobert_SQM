# AstroBobert SQM
tsl2591.py is from https://github.com/jfischer/micropython-tsl2591  
secrets.py contains ssids & passwords for your LAN.  
Example secrets.py file:

```python
SSIDS = 'lan1,lan2,lan3'  
PASSWORDS = 'password1,password2,password3'
```

Note: If your LAN has multipule access points. The last matching ssid in the list will be used to connect.  

main.py is written for Raspberry Pi PicoW with micropython firmware  
(avaiable at https://micropython.org/download/RPI_PICO_W/)  

### THE FOLLOWING COMMENTS WERE MODIFIED FROM chvvkumar GITHUB REPOSITORY
## PiSQM - Sky Quality Meter for Raspberry Pi
Heavily inspired by Richard's work on the ESP platform

https://github.com/rabssm/Radiometer

A Sky Quality Meter implementation for Raspberry Pi using the TSL2591 light sensor. This project measures sky brightness in magnitudes per square arcsecond (MPSAS) and serves readings upon TCP connected request.

## Hardware Requirements
- Raspberry Pi Pico W
- TSL2591 light sensor
- Appropriate housing/enclosure for outdoor use (if applicable)

## Installation
Edit lib.secrets.py as discribed above to use your LAN Ssid and Password prior to uploading to PicoW.

The program will:
1. Connect to LAN as server
2. Initialize the TSL2591 sensor
3. Take measurements upon request
4. Returns readings in Unihedron format  
(avaiable at https://www.unihedron.com/projects/darksky/cd/SQM-LE/SQM-LE_Users_manual.pdf)
5. Print readings to the console

Program runs till shutdown.

## Calibration
The glass attenuation factor (GA) in main.py may need adjustment based on your setup:
GA = 25.55  # Adjust based on your enclosure/setup

- TSL2591 Datasheet: https://ams.com/documents/20143/36005/TSL2591_DS000338_6-00.pdf
- Sky Quality Measurement theory: https://www.mnassa.org.za/html/Oct2017/2017MNASSA..76..Oct..215.pdf
