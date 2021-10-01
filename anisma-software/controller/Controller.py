from serial import Serial, SerialException
import sys, glob
import time
from util.util import *
from enum import Enum
from components.SMASpringParameters import SMASpringParameters
import serial.tools.list_ports

class NodePolarity(Enum):
    OFF = 0
    GND = 1
    VCC = 2

class Controller():
    lastPorts = []

    def newDeviceDetected(self):
        newPorts = Controller.getAvailablePorts()
        if (Controller.lastPorts != newPorts):
            Controller.lastPorts = newPorts
            return True
        
        Controller.lastPorts = newPorts
        return False

    def getAvailablePorts():
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = list(map(lambda x: x.device, list(serial.tools.list_ports.comports())))
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/cu*')
        else:
            raise EnvironmentError('Unsupported platform')

        return ports

    def _resetSerialDevice(serialdev):
        serialdev.setDTR(False)
        time.sleep(1)
        serialdev.flushInput()
        serialdev.setDTR(True)


    def findANISMAControllerDevice(self):
        ports = Controller.getAvailablePorts()
        Controller.lastPorts = ports
        anismaDevicePort = None

        for port in ports:
            try:
                print("checking port", port)
                s = Serial(port)
                # Controller._resetSerialDevice(s)

                starttime = time.time()
                line = ''
                while ((time.time() - starttime) < 0.1):
                    if (s.in_waiting > 0):
                       line = str(s.readline(), 'ascii').replace("\r", "").replace("\n", "")

                linesplit = line.split('-')

                if (len(linesplit) and (linesplit[0] == "anisma")):
                    anismaDevicePort = port
                    print("Found anisma controller ("+linesplit[1]+") at port "+port)
                    s.close()
                    break
                s.close()
            except (OSError, SerialException):
                pass

        return anismaDevicePort

    def __init__(self, port):
        self._port = port
        self._serial = None

    def connect(self, port=None):
        if port is not None:
            self._port = port

        if self._port is not None:
            try:
                self._serial = Serial(self._port)
                print("Connected to port",self._port,".")
            except:
                self._serial = None
                print("Could not connect. Port",self._port,"is not available.")
        else:
            self._serial = None
            print("No device available.")

    def isConnected(self):
        return self._serial is not None

    def allPowerOff(self):
        if self._serial is not None:
            self._serial.write(b'O')

    def setPower(self, pin, mode, power, time, phase):
        if self._serial is not None:
            power = int(power)
            time = int(time)
            dhigh, dlow = time >> 8, time & 0xFF
            self._serial.write(b'N')
            self._serial.write(bytes([pin]))
            self._serial.write(b'H')
            self._serial.write(bytes([phase]))
            self._serial.write(b'P')
            self._serial.write(bytes([power]))
            self._serial.write(b'M')
            self._serial.write(bytes([mode]))
            self._serial.write(b'D')
            self._serial.write(bytes([dlow, dhigh]))

    def initPowerSettings(self):
        if self._serial is not None:
            self._serial.write(b'I')

    def flushPowerSettings(self):
        if self._serial is not None:
            self._serial.write(b'E')

    def getAdjustedPower(self, power, sma):
        result = 0
        smaParams = sma.getSMAParameters()
        if smaParams.getSpringDiameter() == 1.37:
            result =  (8980178 + (2.249992 - 8980178)/(1 + (power/10747.92)**2.808495)) * 3
        elif smaParams.getSpringDiameter() == 2.54:
            result =  11468530 + (2.773747 - 11468530)/(1 + (power/687.4004)**6.43261)+10
        else:
            print("ERROR: UNKNOWN SMA TYPE")
            result =  0

        clip_sma_params = sma.getSMAParameters()

        # get power factor
        pwrfactor = 1.0

        if clip_sma_params.getSpringDiameter() == 1.37:
            # small
            longsma = SMASpringParameters(0.203, 29.13, 1.37, 3.5, 6.5, 30)
            pwrfactor = clip_sma_params.getResistance() / longsma.getResistance()
        elif clip_sma_params.getSpringDiameter() == 2.54:
            # big
            longsma = SMASpringParameters(0.381, 8.27, 2.54, 3.5, 6.5, 16)
            pwrfactor = clip_sma_params.getResistance() / longsma.getResistance()


        return result * pwrfactor

    def setSMAPower(self, sma, power, time):
        if self._serial is not None:
            pwr = int(self.getAdjustedPower(power * 100, sma))
            pin1 = sma.getNodes()[0].getPin()
            pin2 = sma.getNodes()[1].getPin()
            for phase in sma.getPhases():
                self.setPower(pin1, NodePolarity.GND.value, 100, time, phase)
                self.setPower(pin2, NodePolarity.VCC.value, pwr, time, phase)

    def disconnect(self):
        if self._serial is not None:
            self._serial.close()

    def assignPins(self, nodes):
        nodes.sort(key=lambda n: n.getLocation()[1])
        nodes.sort(key=lambda n: n.getLocation()[0])

        for (i,n) in enumerate(nodes):
            n.setPin(i)

    def _assignPolaritiesDeep(self, labeled, node, pol):
        # alternate polarity
        nextPol = NodePolarity.GND
        if pol == NodePolarity.GND:
            nextPol = NodePolarity.VCC

        for c in node.getConnections():
            n = c.getOtherNode(node)

            if n not in labeled:
                n.setPolarity(pol)
                labeled.append(n)
                labeled += self._assignPolaritiesDeep(labeled, n, nextPol)

        return labeled

    def assignPolarities(self, nodes):
        labeled = []

        for n in nodes:
            if n not in labeled:
                n.setPolarity(NodePolarity.GND)
                labeled.append(n)
                labeled += self._assignPolaritiesDeep(labeled, n, NodePolarity.VCC)

        # check collisions
        conns = []
        for n1 in nodes:
            for c in n1.getConnections():
                n2 = c.getOtherNode(n1)

                if (c not in conns) and (n1.getPolarity() == n2.getPolarity()):
                    print("Warning: both nodes of "+c.getName()+" have polarity "+n1.getPolarity().name)

                conns.append(c)

    def assignPhases(self, nodes):
        processedSMAs = []

        # reset phases
        for n in nodes:
            n.resetPhases()
            for c in n.getConnections():
                c.resetPhases()

        # assign phases flat
        for n in nodes:
            for c in n.getConnections():
                if c not in processedSMAs:
                    phasesA = n.getAvailablePhases()
                    oNode = c.getOtherNode(n)
                    phasesB = oNode.getAvailablePhases()

                    phases = listIntersection(phasesA, phasesB)

                    smaParams = c.getSMAParameters()
                    if smaParams.getSpringDiameter() == 1.37:
                        if len(phases) < 1:
                            raise Exception("Phase Assignment failed. Conflicting phase sets.")

                        phase = phases[0]
                        c.assignPhase(phase)
                        n.consumePhase(phase)
                        oNode.consumePhase(phase)
                    elif smaParams.getSpringDiameter() == 2.54:
                        if len(phases) < 2:
                            raise Exception("Phase Assignment failed. Conflicting phase sets.")

                        c.assignPhase(phases[0])
                        c.assignPhase(phases[1])
                        n.consumePhase(phases[0])
                        n.consumePhase(phases[1])
                        oNode.consumePhase(phases[0])
                        oNode.consumePhase(phases[1])

                    processedSMAs.append(c)
