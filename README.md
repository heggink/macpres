# macpres
Domoticz MAC presence detection (ethernet and bluetooth)

To install:
- clone this forder into the domoticz plugins folder
- move the findmac.sh script into /usr/local/bin and make it executable

findmac.sh requires the following utilities to be installed:
- l2ping
- arp-scan

Also, findmac.sh assumes the first 2 octets of your local network to be 192.168. If that's different then edit the file to change this.

When installing and configuring the plugin:
- add the MAC JSON presence plugin
- use a free port on your system for the plugin. It's used to send status messages between the script and the plugin
- you can define multiple MAC addresses for both ethernet and bluetooth. Separate them by a comma.


