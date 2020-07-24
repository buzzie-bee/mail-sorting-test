import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout 
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput

from functools import partial
import time
import socket
import serial
import sys
import threading
from datetime import datetime


class MyApp(App):
    def build(self):
        ##############
        ###############
        thread.start()

        ##############
        ##############
        

        ##
        # Initialise the characters to be selected
        ##
        self.current_string = 'SELECT_CHARS'
        self.string_array = []
        self.initialise_string_array(self.current_string)

        ##############
        # Add text input widget
        ##############
        self.text_input = TextInput(hint_text="Enter character string for selection.")
        self.text_submit_button = Button(text='Submit new code', on_press=self.process_text_input)

        self.text_layout = GridLayout(rows=1, size_hint_y=0.1)
        self.text_layout.add_widget(self.text_input)
        self.text_layout.add_widget(self.text_submit_button)

        #####
        # Create initial character selection
        #####

        self.char_buttons = self.generate_char_buttons(self.current_string)

        ######
        # Stick it all together
        ######
        self.layout = GridLayout(cols=1)
        self.layout.add_widget(self.text_layout)

        # self.layout.add_widget(self.character_select_layout)
        self.layout.add_widget(self.char_buttons)


        # return self.character_select_layout
        return self.layout

    def initialise_string_array(self, string):
        self.string_array = []
        for letter in string:
            self.string_array.append(0)

        print(self.string_array)

    def generate_char_buttons(self, string):
        self.character_select_layout2 = GridLayout(rows=1)
        self.widgets2 = {}
        i=0
        for letter in string:
            self.widgets2[i] = (ToggleButton(text=letter.upper()))
            self.widgets2[i].bind(on_press=partial(self.letter_select, position= i))
            # self.character_select_layout.add_widget(ToggleButton(text=letter))
            self.character_select_layout2.add_widget(self.widgets2[i])
            i += 1 
        self.character_select_layout2.add_widget(Button(text='Process', on_press=self.process))

        return self.character_select_layout2

    def letter_select(self, instance, position=None):
        print('button was pressed!')
        if not position == None:
            print('it was button ', position)
            if self.string_array[position] == 0:
                self.string_array[position] = 1
            else:
                self.string_array[position] = 0
            print(self.string_array)

    def enter_input_text_via_serial(self, received_string):
        self.text_input.text = received_string
        print('setting text!')

    def process_text_input(self, instance):
        print('text input button pressed!')
        print(self.text_input.text)
        text_input_text = self.text_input.text
        if len(text_input_text) > 3:
            self.current_string = text_input_text
            self.initialise_string_array(text_input_text)
            self.update_char_select(text_input_text)
        else:
            print('ERROR! ENTER MORE THAN 3 CHARACTERS')

    def update_char_select(self, new_char_string):
        self.layout.remove_widget(self.char_buttons)
        self.char_buttons = self.generate_char_buttons(new_char_string)
        self.layout.add_widget(self.char_buttons)

    def process(self, instance):
        print('process button was pressed!')
        end = False
        new_preset = ''
        i = 0
        if 1 in self.string_array:
            for position in self.string_array:
                if not end:
                    if position == 0:
                        new_preset += '?'
                    else:
                        end = True
                        new_preset += self.current_string[i]
                        print(position)

                else:
                    if not position == 0:
                        new_preset += self.current_string[i]
                    else:
                        new_preset += '!'
                        break
                i += 1
            print(new_preset)
            print('WP,402,' + bytes.hex(new_preset.encode()))
            preset_command = 'WP,402,' + bytes.hex(new_preset.encode()) + '\r'
            sock.sendall(preset_command.encode('utf-8'))
            print('Preset sent!')
        else:
            print('not ready to process')



class GetStringThreader(threading.Thread):
   #def __init__(self, threadID, name):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        time.sleep(1)

        while True:
            try:
                if not serial_device.inWaiting() > 0:
                    pass
                    #return None
                else:
                    received_string = serial_device.readline().decode().strip()
                    print(received_string)
                    mailapp.enter_input_text_via_serial(received_string)
            except:
                pass
            try:
                data = sock.recv(1024).decode('utf-8')
                returnval = data.strip()
                if returnval[0:6] == 'WP,402':
                    print('PRESETTING!')
                    sock.sendall((returnval + '\r').encode('utf-8'))
                print(returnval[0:6])
                print(returnval)
            except:
                pass

if __name__=='__main__':

##################
    print('Attempting TCP Connecton')

    #Create thread and set it to exit on app close
    thread = GetStringThreader()
    thread.daemon = True
    comms_type = 'none'

    try:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ('192.168.100.101', 9004)
        sock.settimeout(1)
        sock.connect(server_address)
        print('connected!')
        # sock.settimeout(None)
        comms_type = 'tcp'

    except:
        print('Failed to establish TCP Connecton to SR-2000')
        print("Attempting connection to serial device.")
    try:
        #NORMAL RS232 CONNECTION:
        # ser = serial.Serial(
        #     port='COM4',
        #     baudrate=115200,
        #     bytesize=serial.EIGHTBITS,
        #     parity=serial.PARITY_EVEN,
        #     stopbits=serial.STOPBITS_ONE,
        # )

        #USB-COM RS232 CONNECTION
        #used for testing with SRG usb

        serial_device = serial.Serial('COM9')
        print("CONNECTION SUCCESSFUL!")
        comms_type = 'serial'

    except:
        print("Failed to connect to serial port!")

    mailapp = MyApp()
    mailapp.run()

    #On program shutdown, shutdown all sockets and threads
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

    sys.exit()
