from os import error
import serial
import threading
import random


# flag = 11110
class Logic:
    port = serial.Serial()
    data_len = 30
    control_len = 6
    hamming_len = data_len + control_len
    current_output_buffer_len = 0
    output_buffer = ''
    input_buffer = ''


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
                    if self.port.isOpen() == False:
                        break
                    continue
            self.input_buffer += c.decode('utf-8')
            if len(self.input_buffer) == self.hamming_len:
                data = self.decode_hamming(self.input_buffer)
                # self.out_handler(data + '\n')
                self.out_handler(data)
                self.input_buffer = ''

    def write(self, string):
        send_status = False
        if not self.port.isOpen():
            self.debug_handler('Data didn\'t send: port is closed\n')
            return send_status

        if self.current_output_buffer_len + len(string) >= self.data_len:
            self.output_buffer += string[0:self.data_len - self.current_output_buffer_len]
            string = string[self.data_len - self.current_output_buffer_len + 1:]
            output_message = self.encode_hamming(self.output_buffer)
            self.corrupt_data(output_message)
            for c in output_message:
                self.port.write(c.encode('utf-8'))
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

    def corrupt_data(self, data):
        random_val = random.random()
        if random_val < 0.2:
            for i in range(2):
                pos = random.randrange(0, self.hamming_len)
                self.invert_bit_str(data, pos)
        elif random_val < 0.5:
            pos = random.randrange(0, self.hamming_len)
            self.invert_bit_str(data, pos)

    def invert_bit_str(self, str, pos):
        if str[pos] == '0':
            str[pos] = '1'
        else:
            str[pos] = '0'

    def encode_hamming(self, data):
        coded_message = []
        index = 0
        step = 1
        for i in range(self.hamming_len - 1):
            if i + 1 == step:
                coded_message.append(0)
                step *= 2
                continue
            coded_message.append(int(data[index]) - int('0'))
            index += 1
        coded_message.append(0)
        for i in range(self.control_len - 1):
            k = (1 << i) - 1
            while k < len(coded_message) - 1:
                for j in range(1 << i):
                    if k + j >= len(coded_message) - 1:
                        break
                    coded_message[(1 << i) - 1] ^= coded_message[k + j]
                k += (1 << i) * 2
        for i in range(len(coded_message) - 1):
            coded_message[len(coded_message) - 1] ^= coded_message[i]

        hamming_code = [str(i) for i in coded_message]
        return hamming_code

    def decode_hamming(self, data):
        coded_message = [int(i) for i in data]
        coding_bits = [0 for i in range(self.control_len - 1)]
        parity = 0
        for i in range(self.control_len - 1):
            k = (1 << i) - 1
            while k < len(coded_message) - 1:
                for j in range(1 << i):
                    if k + j >= len(coded_message) - 1:
                        break
                    coding_bits[i] ^= coded_message[k + j]
                k += (1 << i) * 2
        for i in range(len(coded_message)):
            parity ^= coded_message[i]
        error_code = 0
        for i, val in enumerate(coding_bits):
            if val:
                error_code += 1 << i
        double_error = False
        if error_code:
            if parity:
                coded_message[error_code - 1] ^= 1
            else:
                double_error = True
        self.output_coding_info(data, error_code, double_error, parity)
        step = 1
        return_data = ''
        for i, c in enumerate(coded_message):
            if i == len(coded_message) - 1:
                break
            if i + 1 == step:
                step *= 2
                continue
            return_data += str(c)
        return return_data

    def output_coding_info(self, data, error_code, double_error, parity):
        step = 1
        coding_data = ''
        for i, c in enumerate(data):
            if i == len(data) - 1:
                self.debug_handler(c, 'bold')
                break
            if i + 1 == step:
                self.debug_handler(c, 'bold')
                coding_data += data[i]
                step *= 2
                continue
            if double_error == False and i == error_code - 1:
                self.debug_handler(c, 'red')
            else:
                self.debug_handler(c)
        coding_data += data[len(data) - 1]
        self.debug_handler(' : ' + str(parity) + ' ' + format(error_code, '05b'))
        if double_error:
            self.debug_handler(' Double error', 'red')
        self.debug_handler('\n')


