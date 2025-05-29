import socket
import threading
import sys
from functools import partial
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
import clkCfg as cc

class ClientLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.input = TextInput(hint_text='Enter command', multiline=False)
        self.output = TextInput(readonly=True)

        self.send_button = Button(text='Send') # Send generic cmd.
        self.send_button.bind(on_press=partial(self.send_command, '')) # New way.

        # GridLayout for "get" command buttons
        self.get_button_grid = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.get_button_grid.bind(minimum_height=self.get_button_grid.setter('height'))

        # Example list of get commands
        get_cmds = [
            ("gas", "Get   Active Style"),
            ("gds", "Get   Day    Style"),
            ("gns", "Get   Night  Style"),
            ("gAs", "Get   ALL    Styles"),
            ("gdt", "Get   Day    Time"),
            ("gnt", "Get   Night  Time"),
            ("gvn", "Get   Version Number"),
            ("gat", "Get   Active Threads"),
            ("close", "Close Connection"),
        ]
        for cmd, label in get_cmds:
            btn = Button(text=label, size_hint_y=None, height=40)
            btn.bind(on_press=partial(self.send_command, cmd))
            self.get_button_grid.add_widget(btn)

        # Add widgets to main layout
        self.add_widget(self.input)
        self.add_widget(self.send_button)
        self.add_widget(self.get_button_grid)
        self.add_widget(self.output)

        scroll = ScrollView()
        self.output = TextInput(readonly=True, size_hint_y=None)
        self.output.bind(minimum_height=self.output.setter('height'))
        scroll.add_widget(self.output)
        self.add_widget(scroll)

        self.cfgDict = cc.getClkCfgDict()
        if self.cfgDict is None:
            print('  Client could not connect to server.')
            print('  Missing or malformed clk.cfg file.')
            sys.exit()

        self.connectDict = {
            's': 'localhost',
            'l': self.cfgDict['myLan'],
            'i': self.cfgDict['myIP']
        }

        self.connectType = 'l'

        ip = self.connectDict[self.connectType]
        port = int(self.cfgDict['myPort'])
        pwd = self.cfgDict['myPwd']

        self.conn = ClientConnection(ip, port, pwd, self.update_output)

    def update_output(self, text):
        Clock.schedule_once(lambda dt: self._update_output_on_main(text))

    def _update_output_on_main(self, text):
        self.output.text += f"\n{text}"
        if "Server killed" in text or "Disconnected" in text:
            self.input.disabled = True
            self.send_button.disabled = True
            for child in self.get_button_grid.children:
                child.disabled = True

    def send_command(self, inText, instance ):

        if instance.text == 'Send':
            cmd = self.input.text.strip()
        else:
            cmd = inText.strip()

        if not cmd:
            return
        self.conn.send_command(cmd)
        self.input.text = ""  # Clear input after sending
#############################################################################
class ClientConnection:
    def __init__(self, ip, port, pwd, on_receive_callback):
        self.ip = ip                # ? Assign to self
        self.port = port
        self.pwd = pwd
        self.socket = None
        self.connected = False
        self.on_receive = on_receive_callback

        # Run connection in background
        threading.Thread(target=self.connect, daemon=True).start()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
            self.socket.send(self.pwd.encode())
            self.connected = True

            response = self.socket.recv(1024).decode()
            self.on_receive(response)
        except Exception as e:
            self.on_receive(f"Connection error: {e}")
            self.connected = False

    def send_command(self, cmd):
        if not self.connected:
            self.on_receive("Not connected.")
            return

        try:
            self.socket.send(cmd.encode())
            self.socket.settimeout(1.0)
            response = ''
            while True:
                try:
                    chunk = self.socket.recv(1024).decode()
                    if not chunk:
                        break
                    response += chunk
                    if 'RE: ks' in response:
                        self.socket.close()
                        self.connected = False
                        self.on_receive("Server killed. Disconnected.")
                        break
                except socket.timeout:
                    break

            self.on_receive(response)

            if cmd.lower() == 'close':
                self.socket.close()
                self.connected = False
                self.on_receive("Disconnected.")
        except Exception as e:
            self.on_receive(f"Send error: {e}")
            self.connected = False

class MyClientApp(App):
    def build(self):
        return ClientLayout()

if __name__ == '__main__':
    MyClientApp().run()

