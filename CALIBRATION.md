## Calibration
I use Putty to establish a telnet connection to the SQM  
Set:  
* Host Name (or IP address) = AstroBobert_SQM (or IP address assigned by your router)
* Port = 10001
* Connection Type = Other/Telnet  

Upon connection if main.py code "client_sock.send(COMMANDS)" is commented out, you will have to type help to see the fellow commans syntax. Otherwiise this command list will display upon connection.
~~~
rxc  = display sensor + config  
rx   = display sensor  
show = display config  
help = display commands  
save = save config  
exit = close connection  
gain [arg] = display/set gain [low, med, high, max]  
time [arg] = display/set time [100, 200, 300, 400, 500, 600]  
m0 [arg]   = display/set m0 factor [defualt -16.07]  
ga [arg]   = display/set glass attenuation factor [default 25.55]  
~~~
