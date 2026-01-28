"""
CuraX Mobile Alert Bot
Android app to receive medication alerts from CuraX desktop software
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
import sqlite3
import json
import socket
import threading
from datetime import datetime
import uuid
import requests

# Set window size for development (ignored on actual Android)
Window.size = (360, 640)


class AlertBotApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_file = 'alerts.db'
        self.bot_id = None
        self.api_key = None
        self.admin_password = None
        self.server_url = "https://curax-alerts.herokuapp.com"  # Cloud server
        self.authenticated = False
        self.running = True
        
    def build(self):
        """Build the app UI"""
        self.init_database()
        self.load_config()
        
        if not self.authenticated:
            return self.create_setup_screen()
        else:
            self.start_alert_checker()
            return self.create_main_screen()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                priority TEXT,
                message TEXT,
                timestamp TEXT,
                read INTEGER DEFAULT 0
            )
        ''')
        
        # Config table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_config(self):
        """Load saved configuration"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM config WHERE key = 'bot_id'")
        result = cursor.fetchone()
        if result:
            self.bot_id = result[0]
        
        cursor.execute("SELECT value FROM config WHERE key = 'api_key'")
        result = cursor.fetchone()
        if result:
            self.api_key = result[0]
            
        cursor.execute("SELECT value FROM config WHERE key = 'admin_password'")
        result = cursor.fetchone()
        if result:
            self.admin_password = result[0]
        
        conn.close()
        
        if self.bot_id and self.api_key and self.admin_password:
            self.authenticated = True
    
    def save_config(self):
        """Save configuration to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                      ('bot_id', self.bot_id))
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                      ('api_key', self.api_key))
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                      ('admin_password', self.admin_password))
        
        conn.commit()
        conn.close()
    
    def create_setup_screen(self):
        """Create first-time setup screen"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = Label(
            text='[color=0099ff]🔐 CuraX Alert Bot Setup[/color]',
            markup=True,
            size_hint_y=0.15,
            font_size='24sp',
            bold=True
        )
        layout.add_widget(header)
        
        # Instructions
        instructions = Label(
            text='Enter your details to set up the alert bot',
            size_hint_y=0.1,
            font_size='14sp'
        )
        layout.add_widget(instructions)
        
        # Bot ID input
        layout.add_widget(Label(text='Bot Name (e.g., My Phone):', size_hint_y=0.08))
        self.bot_name_input = TextInput(
            hint_text='Enter a name for this bot',
            multiline=False,
            size_hint_y=0.1
        )
        layout.add_widget(self.bot_name_input)
        
        # Admin password input
        layout.add_widget(Label(text='Admin Password:', size_hint_y=0.08))
        self.admin_pass_input = TextInput(
            hint_text='Password for deleting alerts',
            password=True,
            multiline=False,
            size_hint_y=0.1
        )
        layout.add_widget(self.admin_pass_input)
        
        # Info box
        info = Label(
            text='[color=666666]After setup, you will receive:\n• Bot ID (to enter in CuraX)\n• API Key (to enter in CuraX)[/color]',
            markup=True,
            size_hint_y=0.15,
            font_size='12sp'
        )
        layout.add_widget(info)
        
        # Setup button
        setup_btn = Button(
            text='Complete Setup',
            size_hint_y=0.12,
            background_color=(0, 0.6, 1, 1),
            bold=True,
            font_size='16sp'
        )
        setup_btn.bind(on_press=self.complete_setup)
        layout.add_widget(setup_btn)
        
        layout.add_widget(Label(size_hint_y=0.12))  # Spacer
        
        return layout
    
    def complete_setup(self, instance):
        """Complete the initial setup"""
        bot_name = self.bot_name_input.text.strip()
        admin_pass = self.admin_pass_input.text.strip()
        
        if not bot_name or not admin_pass:
            self.show_popup('Error', 'Please fill in all fields')
            return
        
        # Generate unique Bot ID and API Key
        self.bot_id = str(uuid.uuid4())[:8].upper()
        self.api_key = str(uuid.uuid4())
        self.admin_password = admin_pass
        
        # Save configuration
        self.save_config()
        
        # Register with cloud server
        self.register_bot()
        
        # Show credentials
        credentials_text = f'''[color=00ff00]✓ Setup Complete![/color]

[b]Enter these in CuraX Desktop:[/b]

[color=0099ff]Bot ID:[/color] {self.bot_id}

[color=0099ff]API Key:[/color]
{self.api_key}

[size=12sp][color=666666]Copy these values and enter them in
CuraX → Settings → Alert Bot[/color][/size]'''
        
        popup = Popup(
            title='Setup Complete',
            content=Label(text=credentials_text, markup=True),
            size_hint=(0.9, 0.7)
        )
        popup.bind(on_dismiss=lambda x: self.switch_to_main())
        popup.open()
    
    def register_bot(self):
        """Register bot with cloud server"""
        try:
            response = requests.post(
                f"{self.server_url}/register",
                json={
                    'bot_id': self.bot_id,
                    'api_key': self.api_key
                },
                timeout=5
            )
            if response.status_code == 200:
                print("✓ Bot registered with cloud server")
        except Exception as e:
            print(f"Cloud registration failed: {e}")
    
    def switch_to_main(self):
        """Switch to main screen"""
        self.authenticated = True
        self.root.clear_widgets()
        self.root.add_widget(self.create_main_screen())
        self.start_alert_checker()
    
    def create_main_screen(self):
        """Create main alert display screen"""
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=0.15,
            padding=10,
            spacing=5
        )
        header_bg = BoxLayout()
        header_bg.canvas.before.clear()
        with header_bg.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0.6, 1, 1)
            self.header_rect = Rectangle(pos=header_bg.pos, size=header_bg.size)
        header_bg.bind(pos=self.update_rect, size=self.update_rect)
        
        header_label = Label(
            text='📱 CuraX Alerts',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        header_bg.add_widget(header_label)
        
        bot_id_label = Label(
            text=f'Bot ID: {self.bot_id}',
            font_size='12sp',
            size_hint_y=0.3,
            color=(0.8, 0.9, 1, 1)
        )
        
        header.add_widget(header_bg)
        header.add_widget(bot_id_label)
        layout.add_widget(header)
        
        # Alerts scroll area
        self.alerts_scroll = ScrollView(size_hint_y=0.75)
        self.alerts_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10,
            size_hint_y=None
        )
        self.alerts_layout.bind(minimum_height=self.alerts_layout.setter('height'))
        self.alerts_scroll.add_widget(self.alerts_layout)
        layout.add_widget(self.alerts_scroll)
        
        # Bottom buttons
        bottom_bar = BoxLayout(size_hint_y=0.1, spacing=5, padding=5)
        
        refresh_btn = Button(
            text='🔄 Refresh',
            background_color=(0.2, 0.7, 0.2, 1)
        )
        refresh_btn.bind(on_press=lambda x: self.refresh_alerts())
        bottom_bar.add_widget(refresh_btn)
        
        clear_btn = Button(
            text='🗑️ Clear All',
            background_color=(0.9, 0.3, 0.3, 1)
        )
        clear_btn.bind(on_press=self.clear_all_alerts)
        bottom_bar.add_widget(clear_btn)
        
        layout.add_widget(bottom_bar)
        
        # Load alerts
        Clock.schedule_once(lambda dt: self.refresh_alerts(), 0.1)
        
        return layout
    
    def update_rect(self, instance, value):
        """Update rectangle size"""
        if hasattr(self, 'header_rect'):
            self.header_rect.pos = instance.pos
            self.header_rect.size = instance.size
    
    def refresh_alerts(self):
        """Refresh alert display"""
        self.alerts_layout.clear_widgets()
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, alert_type, priority, message, timestamp
            FROM alerts
            ORDER BY id DESC
            LIMIT 50
        """)
        alerts = cursor.fetchall()
        conn.close()
        
        if not alerts:
            no_alerts = Label(
                text='[color=999999]No alerts yet\nWaiting for messages from CuraX...[/color]',
                markup=True,
                size_hint_y=None,
                height=100
            )
            self.alerts_layout.add_widget(no_alerts)
            return
        
        for alert_id, alert_type, priority, message, timestamp in alerts:
            self.create_alert_bubble(alert_type, priority, message, timestamp)
    
    def create_alert_bubble(self, alert_type, priority, message, timestamp):
        """Create a chat-style alert bubble"""
        # Determine color based on priority
        if priority == 'CRITICAL':
            bg_color = (0.9, 0.2, 0.2, 1)  # Red
            text_color = (1, 1, 1, 1)
        elif priority == 'HIGH':
            bg_color = (1, 0.6, 0, 1)  # Orange
            text_color = (1, 1, 1, 1)
        else:
            bg_color = (0.2, 0.7, 0.2, 1)  # Green
            text_color = (1, 1, 1, 1)
        
        # Create bubble container
        bubble = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            padding=5
        )
        
        # Create inner bubble with background
        inner = BoxLayout(orientation='vertical', padding=10, spacing=5)
        with inner.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*bg_color)
            self.bubble_rect = RoundedRectangle(
                pos=inner.pos,
                size=inner.size,
                radius=[10]
            )
        inner.bind(pos=lambda inst, val: setattr(self.bubble_rect, 'pos', val),
                  size=lambda inst, val: setattr(self.bubble_rect, 'size', val))
        
        # Alert type header
        header_label = Label(
            text=f'[b]{alert_type}[/b]',
            markup=True,
            size_hint_y=0.3,
            color=text_color,
            font_size='14sp'
        )
        inner.add_widget(header_label)
        
        # Message
        message_label = Label(
            text=message,
            size_hint_y=0.5,
            color=text_color,
            font_size='13sp',
            text_size=(Window.width - 60, None)
        )
        inner.add_widget(message_label)
        
        # Timestamp
        time_label = Label(
            text=timestamp,
            size_hint_y=0.2,
            color=(1, 1, 1, 0.7),
            font_size='10sp'
        )
        inner.add_widget(time_label)
        
        bubble.add_widget(inner)
        self.alerts_layout.add_widget(bubble)
    
    def start_alert_checker(self):
        """Start background thread to check for new alerts"""
        def check_alerts():
            while self.running:
                try:
                    # Poll cloud server for new alerts
                    response = requests.get(
                        f"{self.server_url}/alerts/{self.bot_id}",
                        headers={'X-API-Key': self.api_key},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        alerts = response.json().get('alerts', [])
                        for alert in alerts:
                            self.save_alert(
                                alert['alert_type'],
                                alert['message'],
                                alert['priority']
                            )
                        
                        if alerts:
                            Clock.schedule_once(lambda dt: self.refresh_alerts(), 0)
                
                except Exception as e:
                    print(f"Alert check error: {e}")
                
                # Check every 5 seconds
                import time
                time.sleep(5)
        
        threading.Thread(target=check_alerts, daemon=True).start()
    
    def save_alert(self, alert_type, message, priority):
        """Save alert to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO alerts (alert_type, priority, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (alert_type, priority, message, timestamp))
        
        conn.commit()
        conn.close()
        
        print(f"New alert saved: {alert_type}")
    
    def clear_all_alerts(self, instance):
        """Clear all alerts with password verification"""
        # Create password popup
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Enter admin password to clear alerts:'))
        
        password_input = TextInput(
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        content.add_widget(password_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        popup = Popup(
            title='Admin Verification',
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def verify(inst):
            if password_input.text == self.admin_password:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM alerts")
                conn.commit()
                conn.close()
                
                popup.dismiss()
                self.refresh_alerts()
                self.show_popup('Success', 'All alerts cleared')
            else:
                self.show_popup('Error', 'Incorrect password')
        
        confirm_btn = Button(text='Clear All')
        confirm_btn.bind(on_press=verify)
        btn_layout.add_widget(confirm_btn)
        
        cancel_btn = Button(text='Cancel')
        cancel_btn.bind(on_press=popup.dismiss)
        btn_layout.add_widget(cancel_btn)
        
        content.add_widget(btn_layout)
        popup.open()
    
    def show_popup(self, title, message):
        """Show a simple popup message"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def on_stop(self):
        """Clean up when app closes"""
        self.running = False


if __name__ == '__main__':
    AlertBotApp().run()
