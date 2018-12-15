# coding=utf-8
from __future__ import absolute_import

__author__ = "Jarek Szczepanski <imrahil@imrahil.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2014 Jarek Szczepanski - Released under terms of the AGPLv3 License"

import octoprint.plugin
from octoprint.util import RepeatedTimer
import sys
import re

class NavBarPlugin(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self.isRaspi = False
        self.isAwinner = False
        self.piSocTypes = (["BCM2708", "BCM2709", "BCM2835"]) #Array of raspberry pi SoC's to check against, saves having a large if/then statement later
        self.debugMode = False      # to simulate temp on Win/Mac
        self.displayRaspiTemp = True
        self._checkTempTimer = None

    def on_after_startup(self):
        self.displayRaspiTemp = self._settings.get(["displayRaspiTemp"])
        self.piSocTypes = self._settings.get(["piSocTypes"])
        self._logger.debug("displayRaspiTemp: %s" % self.displayRaspiTemp)

        if sys.platform == "linux2":
            with open('/proc/cpuinfo', 'r') as infile:
                    cpuinfo = infile.read()
            # Match a line like 'Hardware   : BCM2709'
            match = re.search('Hardware\s+:\s+(\w+)', cpuinfo, flags=re.MULTILINE | re.IGNORECASE)

            if match is None:
                # Couldn't find the hardware, assume it isn't a SBC.
                self.isRaspi = False
                self.isAwinner = False
                self._logger.info("No hardware match found")
            elif match.group(1) in self.piSocTypes:
                self._logger.info("Broadcom detected")
                self.isRaspi = True
            elif match.group(1) == 'ODROID-XU3':
                self._logger.info("Awinner detected")
                self.isAwinner = True

            if self.isRaspi and self.displayRaspiTemp:
                self._logger.debug("Let's start RepeatedTimer!")
                self.startTimer(30.0)
            if self.isAwinner and self.displayRaspiTemp:
                self._logger.debug("Let's start RepeatedTimer!")
                self.startTimer(30.0)
        #debug mode doesn't work if the OS is linux on a regular pc
        elif self.debugMode:
            self.isRaspi = True
            if self.displayRaspiTemp:
                self.startTimer(5.0)

        self._logger.debug("is Raspberry Pi? - %s" % self.isRaspi)

    def startTimer(self, interval):
        self._checkTempTimer = RepeatedTimer(interval, self.checkRaspiTemp, None, None, True)
        self._checkTempTimer.start()

    def checkRaspiTemp(self):
        from sarge import run, Capture

        self._logger.debug("Checking Raspberry Pi internal temperature")
        #do we really need to check platform == linux2? aren't these only called if the device has already
        #been determined to be compatible?
        if sys.platform == "linux2": 
            if self.isAwinner:
                p = run("cat /sys/devices/virtual/thermal/thermal_zone0/temp", stdout=Capture()) #this assumes an armbian OS, not sure if there's a universal way to check allwinner SoC temps on every possible OS
            elif self.isRaspi:
                p = run("/opt/vc/bin/vcgencmd measure_temp", stdout=Capture())
            if p.returncode==1:
                self.isAwinner = False
                self.isRaspi = False
                self._logger.info("SoC temperature not found.")
            else:
                p = p.stdout.text

        elif self.debugMode: #doesn't work on linux
            import random
            def randrange_float(start, stop, step):
                return random.randint(0, int((stop - start) / step)) * step + start
            p = "temp=%s'C" % randrange_float(5, 60, 0.1)

        self._logger.debug("response from sarge: %s" % p)

        if self.isRaspi:
            match = re.search('=(.*)\'', p)
        elif self.isAwinner:
            match = re.search('(\d+)', p)
        
        if not match:
            self.isRaspi = False
            self.isAwinner = False
        else:
            if self.isAwinner:
                temp = float(match.group(1))/1000
            else:
                temp = match.group(1)
            self._logger.debug("match: %s" % temp)
            self._plugin_manager.send_plugin_message(self._identifier, dict(israspi=self.isRaspi,isawinner=self.isAwinner, raspitemp=temp))


	##~~ SettingsPlugin
    def get_settings_defaults(self):
        return dict(displayRaspiTemp = self.displayRaspiTemp,
                    piSocTypes = self.piSocTypes)

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        self.displayRaspiTemp = self._settings.get(["displayRaspiTemp"])

        if self.displayRaspiTemp:
            interval = 5.0 if self.debugMode else 30.0
            self.startTimer(interval)
        else:
            if self._checkTempTimer is not None:
                try:
                    self._checkTempTimer.cancel()
                except:
                    pass
            self._plugin_manager.send_plugin_message(self._identifier, dict())

	##~~ TemplatePlugin API
    def get_template_configs(self):
        if self.isRaspi or self.isAwinner:
            return [
                dict(type="settings", template="navbartemp_settings_raspi.jinja2")
            ]
        else:
            return []

    ##~~ AssetPlugin API
    def get_assets(self):
        return {
            "js": ["js/navbartemp.js"],
            "css": ["css/navbartemp.css"],
            "less": ["less/navbartemp.less"]
        } 

    ##~~ Softwareupdate hook
    def get_update_information(self):
        return dict(
            navbartemp=dict(
                displayName="Navbar Temperature Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="ntoff",
                repo="OctoPrint-NavbarTemp",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/ntoff/OctoPrint-NavbarTemp/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "Navbar Temperature Plugin (ntoff mod)"
__plugin_author__ = "ORION_PT (modified by orion_pt)"
__plugin_url__ = "https://github.com/orionpt/OctoPrint-NavbarTemp"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = NavBarPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
