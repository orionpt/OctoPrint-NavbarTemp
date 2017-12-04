# Plugin for OctoPrint - displays temperatures on navbar

Changed in my version:
* Added detection for Armbian OS on Allwinner SoC (specifically a PCDuino3b).
* Reworded some stuff to be less specific to raspberry pi's (changed raspi to SoC, etc)

(Screenshots are from the standard version)


![NavbarTemp](navbar.png?raw=true) 

For Raspberry Pi users it's possible to display internal temperature (configurable via settings dialog):
![NavbarTempRaspi](navbar_raspi.png?raw=true) 



## Setup
My modified version isn't available in the plugin repository, manual setup is required using this URL:

    https://github.com/ntoff/OctoPrint-NavbarTemp/archive/master.zip