from os import error
import serial
from serial.serialutil import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
import threading

class Logic:
    port = serial.Serial()
    def __init__(self, debug_handler, out_handler) -> None:
        errors = 0
        port_interfaces = ('COM1', 'COM2')
        self.debug_handler, self.out_handler = debug_handler, out_handler
        for i in port_interfaces:
            try:
                self.port = serial.Serial(i)
                self.debug_handler("Port {} has opened\n".format(i))
                thread = threading.Thread(target=self.read)
                thread.start()
                return
            except IOError:
                errors += 1
                if error == len(port_interfaces):
                    self.debug_handler("[ERROR] Port's can't be opened!\n")


    def close(self):
        if self.port.isOpen() == True:
            self.port.close()

    def read(self):
        message = bytes()
        while True:
            reading_buffer = self.port.read(1)
            if len(reading_buffer) == 0:
                if self.port.isOpen() != True:
                    break
                continue
            if reading_buffer == b'\x00':
                self.out_handler(message)
                message = bytes()
            else:
                message += reading_buffer
        
    def write(self, string):
        if self.port.isOpen() == False:
            self.debug_handler("Data didn't send: port is closed\n")
            return False
        for c in string:
            self.port.write(c.encode('utf-8'))
        self.port.write('\0'.encode('utf-8'))
        return True

    def switch_baudrate(self, new_baudrate):
        if self.port.isOpen() == False:
            self.debug_handler("Can't switch baudrate: port is closed\n")
            return
        if self.port.baudrate == new_baudrate:
            return
        self.port.baudrate = new_baudrate
        self.debug_handler('New baudrate is {}\n'.format(self.port.baudrate))