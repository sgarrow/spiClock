import re
import socket
import threading
import sys
from functools import partial
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform
from kivy.metrics import dp
import clkCfg as cc

class ClientLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # Input bar
        height = dp(60) if platform == 'android' else 40
        self.input = TextInput(hint_text='Enter command', multiline=False, size_hint_y=None, height=height)
        self.set_input = TextInput(hint_text='Enter value', multiline=False, size_hint_y=None, height=height)
        self.send_button = Button(text='Send')
        self.send_button.bind(on_press=partial(self.send_command, ''))

        #######################
        # Add both inputs to layout, but hide them by default
        self.input.opacity = 0
        self.input.disabled = True
        
        self.set_input.opacity = 0
        self.set_input.disabled = True
        
        self.send_button = Button(text='Send')
        self.send_button.bind(on_press=partial(self.send_command, ''))
        #######################

        # TabbedPanel setup
        self.tabbed_panel = TabbedPanel(do_default_tab=False)

        # --- GET tab ---
        self.get_tab_content = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.get_tab_content.bind(minimum_height=self.get_tab_content.setter('height'))
        get_scroll = ScrollView(size_hint=(1, 1))
        get_scroll.add_widget(self.get_tab_content)
        self.get_tab = TabbedPanelItem(text="Get")
        self.get_tab.add_widget(get_scroll)

        # --- SET tab ---
        self.set_tab_content = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.set_tab_content.bind(minimum_height=self.set_tab_content.setter('height'))
        set_scroll = ScrollView(size_hint=(1, 1))
        set_scroll.add_widget(self.set_tab_content)
        self.set_tab = TabbedPanelItem(text="Set")
        self.set_tab.add_widget(set_scroll)

        # --- OTHER tab ---
        self.oth_tab_content = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.oth_tab_content.bind(minimum_height=self.oth_tab_content.setter('height'))
        oth_scroll = ScrollView(size_hint=(1, 1))
        oth_scroll.add_widget(self.oth_tab_content)
        self.oth_tab = TabbedPanelItem(text="Other")
        self.oth_tab.add_widget(oth_scroll)

        # --- DEBUG tab ---
        self.debug_tab = TabbedPanelItem(text="Debug")
        self.debug_tab.add_widget(Label(text="Type commands below and hit Send"))
        self.tabbed_panel.add_widget(self.debug_tab)

        # Add tabs to the panel
        self.tabbed_panel.add_widget(self.get_tab)
        self.tabbed_panel.add_widget(self.set_tab)
        self.tabbed_panel.add_widget(self.oth_tab)

        # Output (read-only) wrapped in scrollview
        self.output = TextInput(readonly=True, size_hint_y=None)
        self.output.bind(minimum_height=self.output.setter('height'))
        output_scroll = ScrollView(size_hint=(1, 1))
        output_scroll.add_widget(self.output)

        # Final layout structure
        self.add_widget(self.input)
        self.add_widget(self.set_input)
        self.add_widget(self.send_button)
        self.add_widget(self.tabbed_panel)
        self.add_widget(output_scroll)

        # Now that tabbed panel is fully constructed.
        self.tabbed_panel.bind(current_tab=self.on_tab_switch)


        # Config and Connection
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
    ###################

    def update_output(self, text):
        Clock.schedule_once(lambda dt: self._update_output_ui_safe(text))
    ###################

    def _update_output_ui_safe(self, text):
        self.output.text += f"\n{text}"

        if 'CLOCK COMMANDS' in text:
            menu_lines = text.splitlines()
            for line in menu_lines:
                match = re.match(r"\s*(\w+)\s*-\s*(.+)", line)
                if match:
                    cmd, desc = match.groups()
                    self.add_command_button(cmd, desc)
    
        if "Server killed" in text or "Disconnected" in text:
            self.input.disabled = True
            self.send_button.disabled = True
            for tab_content in [self.get_tab_content, self.set_tab_content, self.oth_tab_content]:
                for child in tab_content.children:
                    child.disabled = True
    ###############

    def add_command_button(self, cmd, label):
        # Use taller buttons on Android
        height = dp(60) if platform == 'android' else 40
        btn = Button(text=label, size_hint_y=None, height=height)
        btn.bind(on_press=partial(self.send_command, cmd))
    
        if "Get" in label:
            self.get_tab_content.add_widget(btn)
        elif "Set" in label:
            self.set_tab_content.add_widget(btn)
        else:
            self.oth_tab_content.add_widget(btn)
    ###################

    def on_tab_switch(self, instance, tab):
        if tab.text == "Debug":
            self.input.opacity = 1
            self.input.disabled = False
            self.set_input.opacity = 0
            self.set_input.disabled = True
        elif tab.text in ["Set", "Other"]:
            self.input.opacity = 0
            self.input.disabled = True
            self.set_input.opacity = 1
            self.set_input.disabled = False
        else:  # "Get" or unknown
            self.input.opacity = 0
            self.input.disabled = True
            self.set_input.opacity = 0
            self.set_input.disabled = True
    ###################

    def send_command(self, inText, instance):
        cmd = ""
        if instance.text == 'Send':
            if self.tabbed_panel.current_tab.text == "Debug":
                cmd = self.input.text.strip()
            else:
                cmd = self.set_input.text.strip()
        else:
            # Button-based command
            cmd = inText.strip()
            if self.tabbed_panel.current_tab.text in ["Set", "Other"]:
                param = self.set_input.text.strip()
                if param:
                    cmd += f" {param}"
        if not cmd:
            return
        self.conn.send_command(cmd)
        self.input.text = ""
        self.set_input.text = ""
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
            self.send_command("m") # For auto-populating get buttons.
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

