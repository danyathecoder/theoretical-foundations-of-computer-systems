from os import error
import serial
import threading
import random
import time



class Logic:
    port = serial.Serial()
    data_len = 30
    current_output_buffer_len = 0
    output_buffer = ''
    input_buffer = ''
    channel_busy_probability = 0.2
    collision_probability = 0.5
    jam_signal = '1010'
    max_attempt_number = 10
    slot_time = 0.01

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
        if self.port.isOpen():
            self.port.close()

    def read(self):
        while 1:
            try:
                c = self.port.read(1)
            finally:
                if len(c) == 0:
                    if not self.port.isOpen():
                        break
                    continue
            self.input_buffer += c.decode('utf-8')
            if len(self.input_buffer) == self.data_len:
                jam_signal_buffer = ''
                for i in range(len(self.jam_signal)):
                    try:
                        c = self.port.read(1)
                    finally:
                        if len(c) == 0:
                            break
                    jam_signal_buffer += c.decode('utf-8')
                if jam_signal_buffer != self.jam_signal:
                    self.out_handler(self.input_buffer)
                self.input_buffer = ''

    def write(self, string):
        send_status = False
        if not self.port.isOpen():
            self.debug_handler('Data didn\'t sent: port is closed\n')
            return send_status

        if self.current_output_buffer_len + len(string) >= self.data_len:
            self.output_buffer += string[0:self.data_len - self.current_output_buffer_len]
            string = string[self.data_len - self.current_output_buffer_len + 1:]
            attemps_number = self.transmit_CSMA_CD(self.output_buffer)
            collision_output_str = '*' * attemps_number
            self.debug_handler(self.output_buffer + ' : ' + collision_output_str + '\n')
            self.output_buffer = ''
            self.current_output_buffer_len = 0
            send_status = True

        self.current_output_buffer_len += len(string)
        self.output_buffer += string
        return send_status

    def switch_baudrate(self, new_baudrate):
        if not self.port.isOpen():
            self.debug_handler("Can't switch baudrate: port is closed\n")
            return
        if self.port.baudrate == new_baudrate:
            return
        self.port.baudrate = new_baudrate
        self.debug_handler('New baudrate is {}\n'.format(self.port.baudrate))

    def transmit_CSMA_CD(self, frame):
        attempt_counter = 0
        while 1:
            while not self.is_channel_free():
                pass
            for c in frame:
                self.port.write(c.encode('utf-8'))
            if not self.is_collision():
                break
            for c in self.jam_signal:
                self.port.write(c.encode('utf-8'))
            attempt_counter += 1
            if attempt_counter == self.max_attempt_number:
                return attempt_counter
            self.wait_backoff(attempt_counter)
        return attempt_counter

    def is_channel_free(self):
        random_val = random.random()
        if random_val < self.channel_busy_probability:
            return False
        return True

    def is_collision(self):
        random_val = random.random()
        if random_val < self.collision_probability:
            return True
        return False

    def wait_backoff(self, attempt_number):
        random_val = random.randrange(0, 2 ** min(attempt_number, 10) + 1)
        time.sleep(random_val * self.slot_time)








