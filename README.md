# macpres
Domoticz MAC presence detection (ethernet and bluetooth)

To install:
- clone this forder into the domoticz plugins folder
- move the findmac.sh script into /usr/local/bin and make it executable

findmac.sh requires the following utilities to be installed:
- l2ping
- arp-scan

Also, findmac.sh assumes the first 2 octets of your local network to be 192.168. If that's different then edit the file to change this.
