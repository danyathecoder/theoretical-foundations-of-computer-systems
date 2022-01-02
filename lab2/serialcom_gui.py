from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import Separator
from tkinter.ttk import Combobox

from serialcom_logic import Logic


class GUI:
    master_min_width, master_min_height = 800, 768
    master_max_width, master_max_height = 1024, 768
    master_background_color = '#C0C0C0'
    scrolled_text_height = 10
    header_font = ("Times New Roman", 14)
    label_font = ("Times New Roman", 12)
    deafult_baudrate = 9600
    uart_baudrates = [110, 150, 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

    def __init__(self, master) -> None:

        # configuring master window
        self.master = master
        master.title("Serial port communicator")
        master.geometry("800x768")
        master.minsize(self.master_min_width, self.master_min_height)
        master.maxsize(self.master_max_width, self.master_max_height)
        master.configure(bg=self.master_background_color)
        master.protocol("WM_DELETE_WINDOW", self._close_handler)

        # input frame
        frame_in = self._create_labeled_frame(self.master, "Input", "top")

        self.text_in = scrolledtext.ScrolledText(frame_in, height=self.scrolled_text_height)
        self.text_in.bind('<<Modified>>', self._input_handler)
        self.text_in.pack(expand=1, fill='x', padx=20)

        bindtags = list(self.text_in.bindtags())
        bindtags.remove("Text")
        self.text_in.bindtags(tuple(bindtags))
        self.text_in.bind('<Key-1>', lambda e, k='1': self._key_trigger(e, k))
        self.text_in.bind('<Key-0>', lambda e, k='0': self._key_trigger(e, k))
        self.text_in.bind('<Button-1>', lambda e: e.widget.focus_set())

        self._create_separator(self.master)

        # output frame
        frame_out = self._create_labeled_frame(self.master, "Output", "top")

        self.text_output = scrolledtext.ScrolledText(frame_out,
                                                     height=self.scrolled_text_height,
                                                     state='disabled')
        self.text_output.pack(expand=1, fill='x', padx=20)

        self._create_separator(self.master)

        # debug frame
        frame_control = self._create_labeled_frame(self.master, "Control & Debug", "top")
        frame_baudrate = self._create_labeled_frame(frame_control, "Baudrate", "left", "center")

        combo = Combobox(frame_baudrate, state='readonly')
        combo['values'] = self.uart_baudrates
        combo.current(self.uart_baudrates.index(self.deafult_baudrate))
        combo.pack(padx=20)
        combo.bind('<<ComboboxSelected>>', self._baudrate_handler)

        frame_debug_text = Frame(frame_control, bg=self.master_background_color)
        frame_debug_text.pack(side='right', expand=1, fill='x')

        self.text_debug = scrolledtext.ScrolledText(frame_debug_text, height=self.scrolled_text_height / 2, state='disabled')
        self.text_debug.pack(expand=1, fill='x', padx=20)

        self.text_send = scrolledtext.ScrolledText(frame_debug_text, height=self.scrolled_text_height / 2, state='disabled')
        self.text_send.pack(expand=1, fill='x', padx=20)
        self.text_send.tag_config('red', foreground='red')

        self.backend = Logic(self._debug_handler, self._output_handler, self._sended_text_handler)

    def _create_separator(self, master):
        sep = Separator(master, orient='horizontal')
        sep.pack(expand=1, fill='x')

    def _create_labeled_frame(self, master_frame, text_var, side_var, anchor_var=None) -> Frame:
        frame = Frame(master_frame, bg=self.master_background_color)
        label = Label(frame, text=text_var, font=self.header_font, bg=self.master_background_color)
        label.pack(expand=1, fill='x', padx=20, side='top', pady=5)
        frame.pack(side=side_var, expand=1, anchor=anchor_var)
        return frame

    def _close_handler(self):
        self.backend.close()
        self.master.destroy()

    def _input_handler(self, event):
        if event.widget.edit_modified() == 0:
            return
        char = event.widget.get("end-2c", 'end-1c')
        result = self.backend.write(char)
        if result == True:
            event.widget.edit_modified(0)

    def _baudrate_handler(self, event):
        baudrate = int(event.widget.get())
        self.backend.switch_baudrate(baudrate)

    def _debug_handler(self, string):
        self.text_debug.config(state='normal')
        self.text_debug.insert('end-1c', string)
        self.text_debug.see(END)
        self.text_debug.config(state='disabled')

    def _output_handler(self, message):
        self.text_output.config(state='normal')
        self.text_output.insert('end-1c', message)
        self.text_output.see(END)
        self.text_output.config(state='disabled')

    def _sended_text_handler(self, string, color = 'black'):
        self.text_send.config(state='normal')
        self.text_send.insert('end-1c', string)
        self.text_send.see(END)
        if color == 'red':
            self.text_send.tag_add('red', 'end-2c')
        self.text_send.config(state='disabled')

    def _key_trigger(self, event, key):
        event.widget.insert(END, key)
        event.widget.see(END)
