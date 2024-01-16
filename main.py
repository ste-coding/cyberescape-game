#to finish:
#final page and how to play page, design, phase 2 check decrypted message, phase 3 texts and transiton
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRoundFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import StringProperty

import functools
import random

#homepage
class HomePage(Screen):
    pass

#how to pplay page (add instructions)
class HowToPlay(Screen):
    pass
#phase1: basically a quiz (maybe use a database to randomize the questions)
class Phase1(Screen):
    timer = NumericProperty(30)

    def on_enter(self): # starts the timer when the screen is entered
        Clock.schedule_interval(self.update_timer, 1)

    def on_pre_leave(self): #stops the timer when leaving the screen
        Clock.unschedule(self.update_timer)

    def update_timer(self, dt): #keeps updating the timer and sends player to final page if not answered in time
        self.timer -= 1
        if self.timer == 0:
            self.manager.current = "final_page"
        else:
            self.ids.timer_label.text = str(self.timer)

    def check_answer(self, selected_answer):
        if selected_answer == "correct":
            self.manager.current = "phase2"
        else:
            self.manager.current = "final_page"

#caeser cypher
class Phase2(Screen):
    timer = NumericProperty(90)
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
            self.manager.current = "final_page"

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
        original_message = "CyberEscape is fun!"
        decrypted_message = self.encrypt_message(self.encrypted_message, 26 - self.shift)

        if input_text == original_message:
            self.manager.current = "phase3"
        else:
            self.manager.current = "final_page"

#case study
class Phase3(Screen):
    timer = NumericProperty(120)
    scenario = StringProperty("")

    def on_enter(self):
        Clock.schedule_interval(self.update_timer, 1)
        self.present_scenario()

    def on_pre_leave(self):
        Clock.unschedule(self.update_timer)

    def update_timer(self, dt):
        self.timer -= 1
        if self.timer == 0:
            self.manager.current = "final_page"

    def present_scenario(self):
        text_scenario = (
            "You find yourself in the cybersecurity control room, tracking an ongoing cyberattack.\n\n"
            "Scenario:\n"
            "A hacker group known as 'DarkByte' is attempting to infiltrate a government server.\n"
            "They have gained access to classified information and left behind clues.\n"
            "Your mission is to track the invader, prevent further damage, and uncover their motives.\n\n"
            "Information:\n"
            "- Target: Government server\n"
            "- Invasion Method: Advanced Persistent Threat (APT)\n"
            "- Clues Left: Cryptic messages in the system logs\n\n"
            "Decisions:\n"
            "1. Analyze system logs to decipher cryptic messages.\n"
            "2. Initiate a counter-attack to block the hacker's access.\n"
            "3. Collaborate with external cybersecurity experts for assistance.\n"
            "4. Disconnect the server from the network to contain the breach."
        )
        
        self.scenario = text_scenario

        #labels to display scenario information (need to review)
        scenario_label = MDLabel(text=text_scenario, font_size="18sp", halign="left", valign="top", markup=True)

        # Create buttons for user decisions
        button1 = MDRaisedButton(text="1. Analyze system logs", size_hint=(None, None), size=(300, 50),
                         pos_hint={"center_x": 0.5}, on_release=self.make_decision)
        button2 = MDRaisedButton(text="2. Initiate a counter-attack", size_hint=(None, None), size=(300, 50),
                         pos_hint={"center_x": 0.5}, on_release=self.make_decision)
        button3 = MDRaisedButton(text="3. Collaborate with experts", size_hint=(None, None), size=(300, 50),
                         pos_hint={"center_x": 0.5}, on_release=self.make_decision)
        button4 = MDRaisedButton(text="4. Disconnect the server", size_hint=(None, None), size=(300, 50),
                         pos_hint={"center_x": 0.5}, on_release=self.make_decision)

        # adds widgets to the screen
        self.add_widget(scenario_label)
        self.add_widget(button1)
        self.add_widget(button2)
        self.add_widget(button3)
        self.add_widget(button4)

    def make_decision(self, instance): #hets uses decision and shows its consequences
        decision_number = int(instance.text.split(".")[0])

        consequences_text = ""
        success = False

        if decision_number == 1:
            #d1: analyze system logs
            consequences_text = (
                "You meticulously analyze the system logs and successfully decipher the cryptic messages.\n"
                "You uncover the hacker's plan and prevent a major data breach.\n"
                "Congratulations! You made the right decision."
            )
            success = True
        elif decision_number == 2:
            #d2: Initiate a counter-attack
            consequences_text = (
                "You initiate a counter-attack, but the hacker outsmarts you and retaliates with a stronger attack.\n"
                "Unfortunately, the counter-attack backfires, leading to more damage.\n"
                "You lost this round. Better luck next time."
            )
        elif decision_number == 3:
            #d3: Collaborate with experts
            consequences_text = (
                "You collaborate with external cybersecurity experts who provide valuable insights and assistance.\n"
                "Together, you successfully thwart the hacker's attempts and secure the server.\n"
                "Congratulations! You made the right decision."
            )
            success = True
        elif decision_number == 4:
            #d4: Disconnect the server
            consequences_text = (
                "You decide to disconnect the server to contain the breach, but it results in data loss and downtime.\n"
                "The hacker takes advantage of the disruption and escapes with sensitive information.\n"
                "You lost this round. Better luck next time."
            )

        
        self.show_consequences(consequences_text, success)

    def show_consequences(self, text, success):
        consequences_label = MDLabel(text=text, font_size="18sp", halign="center", valign="middle", markup=True)
        self.add_widget(consequences_label)

        if success:
            Clock.schedule_once(functools.partial(self.change_screen, "congratulations_page"), 5)
        else:
            Clock.schedule_once(functools.partial(self.change_screen, "sorry_page"), 5)

class FinalPage(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass


class CyberEscapeApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        return Builder.load_file("cyberescape.kv")
    
if __name__ == "__main__":
    CyberEscapeApp().run()

