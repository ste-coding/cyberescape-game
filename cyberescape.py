from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRoundFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.color_definitions import colors


import functools
import random

# homepage


class HomePage(Screen):
    pass

# how to play page (add instructions)


class HowToPlay(Screen):
    pass
# phase1: basically a quiz (maybe use a database to randomize the questions)


class Phase1(Screen):
    timer = NumericProperty(30)

    def on_enter(self): # starts the timer when the screen is entered
        Clock.schedule_interval(self.update_timer, 1)

    def on_pre_leave(self): #stops the timer when leaving the screen
        Clock.unschedule(self.update_timer)

    def update_timer(self, dt): #keeps updating the timer and sends player to final page if not answered in time
        self.timer -= 1
        if self.timer == 0:
            self.manager.current = "lost_page"
        else:
            self.ids.timer_label.text = str(self.timer)

    def check_answer(self, selected_answer):
        if selected_answer == "correct":
            self.manager.current = "phase2"
        else:
            self.manager.current = "lost_page"

#caeser cypher
class Phase2(Screen):
    timer = NumericProperty(600)
    shift = NumericProperty(0)
    encrypted_message = StringProperty("")
    decrypted_message = StringProperty("")

    def on_enter(self):
        Clock.schedule_interval(self.update_timer, 1)
        self.generate_encrypted_message()

    def on_pre_leave(self):
        Clock.unschedule(self.update_timer)

    def update_timer(self, dt):
        self.timer -= 1
        if self.timer == 0:
            self.manager.current = "lost_page"

    def generate_encrypted_message(self):
        original_message = "CyberEscape is fun!"
        self.shift = random.randint(1, 25)
        self.encrypted_message = self.encrypt_message(original_message, self.shift)

    def encrypt_message(self, message, shift):
        encrypted_message = ""
        for char in message:
            if char.isalpha():
                shifted_char = chr((ord(char.lower()) - ord('a') + shift) % 26 + ord('a'))
                encrypted_message += shifted_char if char.islower() else shifted_char.upper()
            else:
                encrypted_message += char
        return encrypted_message

    def check_decryption(self, input_text): #compares input text with original message
        decrypted_message = self.encrypt_message(self.encrypted_message, 26 - self.shift)

        if input_text == decrypted_message:
            self.manager.current = "phase3"
        else:
            self.manager.current = "lost_page"

#case study
class Phase3(Screen):
    timer = NumericProperty(120)
    text_scenario = StringProperty("")

    def on_enter(self):
        Clock.schedule_interval(self.update_timer, 1)
        self.present_scenario()

    def on_pre_leave(self):
        Clock.unschedule(self.update_timer)

    def update_timer(self, dt):
        self.timer -= 1
        if self.timer == 0:
            self.manager.current = "lost_page"
            
    def change_screen(self, screen_name, *args):
        self.manager.current = screen_name

    def present_scenario(self):
        text_scenario = (
            "Yoy find yourself in the cybersecurity control room, tracking an ongoing attack."
            "A hacker group known as 'DarkBit' is attempting to infiltrate a government server with data about 5 million citzens."
            "They have gained access to classified information and left behind clues."
            "Your mission is to track the invader and prevent further damage.\n\n"
            
        "Information:\n"
        "- Target: Government server\n"
        "-Invasion Method: Advanced Persistent Threat (APT)\n"
        "-Clues Left: Cryptic messages in the system logs"
        )
        self.text_scenario = text_scenario
        
    def make_decision(self, decision_number):
        consequences_text = ""
        success = False
        
        if decision_number == 1:
            success = True
            consequences_text = "You meticulously analyze the system logs and successfully decipher the cryptic messages.\n"
            "You uncover the hacker's plan and prevent a major data breach.\n"
            "Congratulations! You made the right decision."
        elif decision_number == 2:
            consequences_text = "You initiate a counter-attack, but the hacker outsmarts you and retaliates with a stronger attack.\n"
            "Unfortunately, the counter-attack backfires, leading to more damage.\n"
            "You lost this round. Better luck next time."
        elif decision_number == 3:
            success: True
            consequences_text =  "You collaborate with external cybersecurity experts who provide valuable insights and assistance.\n"
            "Together, you successfully thwart the hacker's attempts and secure the server.\n"
            "Congratulations! You made the right decision."
        elif decision_number == 4:
            consequences_text = "You decide to disconnect the server to contain the breach, but it results in data loss and downtime.\n"
            "The hacker takes advantage of the disruption and escapes with sensitive information.\n"
            "You lost this round. Better luck next time."

        self.show_consequences(consequences_text, success)

    def show_consequences(self, text, success):
        consequences_label = MDLabel(text=text, font_size="18sp", halign="center", valign="middle", markup=True)
        self.add_widget(consequences_label)

        if success:
            Clock.schedule_once(functools.partial(self.change_screen, "winner_page"), 5)
        else:
            Clock.schedule_once(functools.partial(self.change_screen, "lost_page"), 5)

class LostPage(Screen):
    pass

class WonPage(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass


class CyberEscapeApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        Window.size = (400, 700)
        sm = ScreenManager(transition=SwapTransition())
        sm.add_widget(HomePage(name="homepage"))
        sm.add_widget(HowToPlay(name="how_to_play"))
        sm.add_widget(Phase1(name="phase1"))
        sm.add_widget(Phase2(name="phase2"))
        sm.add_widget(Phase3(name="phase3"))
        sm.add_widget(WonPage(name="winner_page"))
        sm.add_widget(LostPage(name="lost_page"))
        return sm
        return Builder.load_file(filename="cyberescape.kv")
    
if __name__ == "__main__":
    CyberEscapeApp().run()

