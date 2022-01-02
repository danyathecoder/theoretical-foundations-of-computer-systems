from os import error
import serial
import threading


# flag = 00011110
class Logic:
    port = serial.Serial()
    flag = '00011110'
    input_buffer = ''
    output_buffer = ''

    def __init__(self, debug_handler, out_handler, sended_text_handler) -> None:
        errors = 0
        port_interfaces = ('COM1', 'COM2')
        self.debug_handler, self.out_handler, self.sended_text_handler = debug_handler, out_handler, sended_text_handler
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
        if self.port.isOpen():
            self.port.close()

    def read(self):
        while 1:
            try:
                c = self.port.read(1)
            finally:
                if len(c) == 0:
                    if self.port.isOpen() == False:
                        break
                    continue
            c = self.debitstuffing(c.decode('utf-8'))
            self.out_handler(c)

    def write(self, string):
        if not self.port.isOpen():
            self.debug_handler("Data didn't send: port is closed\n")
            return False
        for c in string:
            self.sended_text_handler(c)
            self.bitstuffing(c)
            self.port.write(c.encode('utf-8'))
        return True

    def switch_baudrate(self, new_baudrate):
        if not self.port.isOpen():
            self.debug_handler("Can't switch baudrate: port is closed\n")
            return
        if self.port.baudrate == new_baudrate:
            return
        self.port.baudrate = new_baudrate
        self.debug_handler('New baudrate is {}\n'.format(self.port.baudrate))

    def bitstuffing(self, bit):
        result = ''
        self.input_buffer += bit
        if len(self.input_buffer) > 7:
            self.input_buffer = self.input_buffer[1:]
        if self.input_buffer == self.flag[:7]:
            result = '1'
            self.port.write('1'.encode('utf-8'))
            self.sended_text_handler('1', 'red')
        return result

    def debitstuffing(self, bit):
        self.output_buffer += bit
        if len(self.output_buffer) > 8:
            self.output_buffer = self.output_buffer[1:]
        if self.output_buffer == self.flag[:7] + '1':
            bit = ''
            self.output_buffer = self.output_buffer[:-1]
        return bit
