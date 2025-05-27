from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
import socket
import threading
import clkCfg as cc
import sys

class ClientLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.input = TextInput(hint_text='Enter command', multiline=False)
        self.output = TextInput(readonly=True)
        self.send_button = Button(text='Send')
        self.send_button.bind(on_press=self.send_command)

        self.add_widget(self.input)
        self.add_widget(self.send_button)
        self.add_widget(self.output)

        self.client_socket = None
        self.connected = False

        self.cfgDict     = cc.getClkCfgDict()
        if self.cfgDict is None:
            print('  Client could not connect to server.')
            print('  Missing or malformed clk.cfg file.')
            sys.exit()

        self.connectDict = { 's' : 'localhost',
                             'l' : self.cfgDict['myLan'],
                             'i' : self.cfgDict['myIP' ] }

        self.connectType = 'l'

        self.ip   = self.connectDict[self.connectType]
        self.port = int(self.cfgDict['myPort'])
        self.pwd  = self.cfgDict['myPwd']

        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def update_output(self, text):
        Clock.schedule_once(lambda dt: self._update_output_on_main(text))

    def _update_output_on_main(self, text):
        self.output.text += f"\n{text}"

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.ip, self.port))
            self.connected = True

            # Send password
            self.client_socket.send(self.pwd.encode())

            # Receive initial server response
            response = self.client_socket.recv(1024).decode()
            self.update_output(response)

        except Exception as e:
            self.update_output(f"Connection error: {e}")
            self.connected = False

    def send_command(self, instance):
        if not self.connected:
            self.update_output("Not connected.")
            return

        command = self.input.text.strip()
        if not command:
            return

        try:
            self.client_socket.send(command.encode())

            # Receive response (blocking but short timeout)
            self.client_socket.settimeout(1.0)
            response = ''
            while True:
                try:
                    chunk = self.client_socket.recv(1024).decode()
                    if not chunk:
                        break
                    response += chunk
                    if 'RE: ks' in response:
                        break
                except socket.timeout:
                    break

            self.update_output(response)

            if command.lower() == 'close':
                self.client_socket.close()
                self.connected = False
                self.update_output("Disconnected.")

        except Exception as e:
            self.update_output(f"Send error: {e}")
            self.connected = False

    #def update_output(self, text):
    #    self.output.text += f"\n{text}"

class MyClientApp(App):
    def build(self):
        return ClientLayout()

if __name__ == '__main__':
    MyClientApp().run()

