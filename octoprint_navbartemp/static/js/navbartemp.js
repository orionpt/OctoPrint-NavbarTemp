$(function() {
    function NavbarTempViewModel(parameters) {
        var self = this;

        self.temperatureModel = parameters[0];
        self.global_settings = parameters[1];
        self.socTemp = ko.observable(null);
        /* 
         * raspi and awinner should be combined into something like hasSoc in the python
         * source, there's no need for this part to know or care what the sbc is made of
         * 
         */
        self.isRaspi = ko.observable(false); 
        self.isAwinner = ko.observable(false);
        //hassoc should be taken care of in the python source before it gets this far
        self.hasSoc = ko.pureComputed(function() {
            return self.isRaspi || self.isAwinner;
        });
        
        self.onBeforeBinding = function () {
            self.settings = self.global_settings.settings.plugins.navbartemp;
        };

        self.formatBarTemperature = function(toolName, actual, target) {
            var output = toolName + ": " + _.sprintf("%.1f&deg;C", actual);
        
            if (target) {
                var sign = (target >= actual) ? " \u21D7 " : " \u21D8 ";
                output += sign + _.sprintf("%.1f&deg;C", target);
            }
        
            return output;
        };
        
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "navbartemp") {
                return;
            }
            else {
                self.isRaspi(data.israspi);
                self.isAwinner(data.isawinner);
                self.socTemp(_.sprintf("SoC: %.1f&deg;C", data.raspitemp));
            }
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: NavbarTempViewModel, 
        dependencies: ["temperatureViewModel", "settingsViewModel"],
        elements: ["#navbar_plugin_navbartemp", "#settings_plugin_navbartemp",]
    });
});

