# Plugin for OctoPrint - displays temperatures on navbar

![NavbarTemp](navbar.png?raw=true) 

For Raspberry Pi users it's possible to display internal temperature (configurable via settings dialog):
![NavbarTempRaspi](navbar_raspi.png?raw=true) 

Added detection for Allwinner SoC and assuming armbian OS to display SoC temperature.

## Setup
(note: armbian/awinner soc temperature not available from octoprint plugin repository)

Install ~~via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or~~ manually using this URL:

    https://github.com/ntoff/OctoPrint-NavbarTemp/archive/master.zip