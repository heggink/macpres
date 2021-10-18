# MAC address presence Python Plugin
#
# Author: me
#
# MAC addresses in de format xx:xx:xx:xx:xx:xx,xx:xx:xx:xx:xx:xx,xx:xx:xx:xx:xx:xx
"""
<plugin key="mac" name="MAC JSON presence" author="me" version="0.0.1">
    <params>
        <param field="Mode1" label="TCP Port" width="30px" required="true" default="2452"/>
        <param field="Mode2" label="BTH MAC addresses" width="300px" required="true" default="aa:bb:cc:dd:ee:ff,11:22:33:44:55:66"/>
        <param field="Mode3" label="ETH MAC addresses" width="300px" required="true" default="aa:bb:cc:dd:ee:ff,11:22:33:44:55:66"/>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Python" value="18"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz

#from Domoticz import Devices, Parameters

import os
import json

class BasePlugin:

    def __init__(self):
        self.count=0
        return

    def onStart(self):
        Domoticz.Debug("onStart called")

        self.port=int(Parameters["Mode1"])

        try:
            Domoticz.Debugging(int(Parameters["Mode6"]))
        except ValueError:
            Domoticz.Log("Illegal value for Debug, using default (0)")

        bthmaclist = Parameters['Mode2'].split(',')
        ethmaclist = Parameters['Mode3'].split(',')

        if len(bthmaclist) == 0 and len(ethmaclist) == 0:
            Domoticz.Error("Empty MAClists")
            return

        ef = open("/tmp/ethmacs.cfg", "w")
        for i in ethmaclist:
            proto='ETH'
            mac=i.lower()
            Domoticz.Debug('Found entry. Proto: ' + proto + ' and MAC: ' + i)
            ef.write(mac+'\n')
        ef.close()

        bf = open("/tmp/bthmacs.cfg", "w")
        for i in bthmaclist:
            proto='BTH'
            mac=i.lower()
            Domoticz.Debug('Found entry. Proto: ' + proto + ' and MAC: ' + i)
            bf.write(mac+'\n')
        bf.close()

        self.conn = Domoticz.Connection( Name="PP", Transport="TCP/IP", Protocol="JSON", Address="127.0.0.1", Port=Parameters["Mode1"])
        self.conn.Listen()

        Domoticz.Heartbeat(10)

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        if (Status == 0):
            Domoticz.Debug("Connected successfully to: "+Connection.Address+":"+Connection.Port)
        else:
            Domoticz.Debug("Failed to connect ("+str(Status)+") to: "+Connection.Address+":"+Connection.Port+" with error: "+Description)
        Domoticz.Debug(str(Connection))

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called with: " + str(Data))
        strData = Data.decode("utf-8", "ignore")
        if len(strData) <= 5:
            return

        try:
            jData = json.loads(strData)

        except JSONDecodeError:
            Domoticz.Debug("onMessage received bad data")
            return

        Domoticz.Debug("onMessage has: " + str(jData))

        mac = jData["MAC"]
        state = jData["State"]
        proto = jData["Proto"]
        Domoticz.Debug("Received device update for MAC: "+mac+" proto: "+proto+" and state: "+state)

        num_devices = len(Devices)
        Domoticz.Debug("Number of devices: "+str(num_devices) + " and len: " +str(len(Devices)))
        num=0
        found = False

        while num < num_devices:
            Domoticz.Debug("Iterating through devices: "+str(num+1))
            Domoticz.Debug("Iterating through devices: "+Devices[num+1].Name)
            if Devices[num+1].DeviceID == mac:
                found = True
                Domoticz.Debug("onMessage found existing device: " + str(Devices[num+1].Unit))
                break
            num = num + 1

        if not found:
            Domoticz.Debug("Create device: " + str(num + 1) + " for: " + mac)
            Domoticz.Device(Name=proto+' '+mac, Unit=(num + 1), TypeName="Switch", DeviceID=mac, Used=1).Create()

        if state == "on":
            Domoticz.Debug('Switching device ON: ' + mac)
            UpdateDevice(num+1,1,'On')
        else:
            Domoticz.Debug('Switching device OFF: ' + mac)
            UpdateDevice(num+1,0,'Off')


    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        Command = Command.strip()
        action, sep, params = Command.partition(' ')
        action = action.capitalize()
        params = params.capitalize()

        if Command=='Off':
            UpdateDevice(Unit,0,'Off')
        elif Command=='On':
            UpdateDevice(Unit,1,'On')

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartBeat called "+str(self.count))
        self.count=self.count+1
        if self.count > 5:
            self.count=0
            Domoticz.Debug("onHeartBeat get device status")
            os.popen("findmac.sh "+str(self.port)+"&")
        return

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

################################################################################
# Generic helper functions
################################################################################
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    for x in Settings:
        Domoticz.Debug("Setting:           " + str(x) + " - " + str(Settings[x]))

def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
