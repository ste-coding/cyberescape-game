from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRoundFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.color_definitions import colors
from kivymd.font_definitions import theme_font_styles
import random
from random import choice
import json



class Welcome(Screen):
    def submit_name(self):
        user_name = self.ids.name_input.text.strip()
        if user_name:
            self.manager.user_name = user_name
            self.manager.current = "homepage"


class HomePage(Screen):
    def on_enter(self, *args):
        super().on_enter(*args)
        welcome_label = self.ids.welcome_label
        welcome_label.text = f"Bem-vindo(a), {self.manager.user_name}!"


class HowToPlay(Screen):
    pass


class TimerScreen(Screen):
    timer = NumericProperty(0)

    def on_enter(self):
        Clock.schedule_interval(self.update_timer, 1)

    def on_pre_leave(self):
        Clock.unschedule(self.update_timer)

    def reset_timer(self, initial_time):
        self.timer = initial_time

    def update_timer(self, dt):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.manager.current = "lost_page"


class Phase1(TimerScreen, Screen):
    timer = NumericProperty(30)
    question = StringProperty("")
    options = ListProperty([])
    correct_index = NumericProperty(-1)
    question_label = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.load_question)

    def load_question(self, *args):
        with open('assets/questions_db.json', 'r', encoding='utf-8') as f:
            questions = json.load(f)["questions"]
            selected_question = random.choice(questions)
            self.question = selected_question["question"]
            self.options = selected_question["options"]
            self.correct_index = selected_question["correct"]
        
        self.ids.question_label.text = self.question
        self.create_answer_buttons()

    def create_answer_buttons(self):
        answers_layout = self.ids.answers_layout
        answers_layout.clear_widgets()
        for index, option in enumerate(self.options):
            button = MDRaisedButton(
                text=option,
                size_hint=(None, None),
                size=(200, 48),
                pos_hint={"center_x": 0.5},
                on_release=lambda x, idx=index: self.check_answer(idx)
            )
            answers_layout.add_widget(button)

    def check_answer(self, selected_index):
        if selected_index == self.correct_index:
            self.manager.current = "phase2"
        else:
            self.manager.current = "lost_page"


def encrypt_message(message, shift):
    encrypted_message = ""
    for char in message:
        if char.isalpha():
            shifted_char = chr((ord(char.lower()) - ord('a') + shift) % 26 + ord('a'))
            encrypted_message += shifted_char if char.islower() else shifted_char.upper()
        else:
            encrypted_message += char
    return encrypted_message


class Phase2(TimerScreen, Screen):
    timer = NumericProperty(180)
    shift = NumericProperty(0)
    encrypted_message = StringProperty("")
    original_message = StringProperty("Sistemas seguros")
    info_label = StringProperty("")
    input_text = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_text = MDTextField(
            hint_text="Digite a mensagem encriptada",
            multiline=False,
            pos_hint={"center_x": 0.5, "center_y": 0.35},
            on_text_validate=self.check_encryption,
            size_hint_x=0.8,
        )
        self.add_widget(self.input_text)

    def on_enter(self):
        super().on_enter()
        self.generate_encrypted_message()

    def on_leave(self, *args):
        self.reset_phase2()

    def reset_phase2(self):
        self.reset_timer(120)
        self.input_text.text = ""

    def generate_encrypted_message(self):
        self.shift = random.randint(1, 25)
        self.encrypted_message = encrypt_message(self.original_message, self.shift)

        self.info_label = f"Shift: {self.shift}\n {self.original_message}"

    def check_encryption(self):
        input_text = self.input_text.text.strip()
        if input_text == self.encrypted_message:
            self.manager.current = "phase3"
        else:
            self.manager.current = "lost_page"


class Phase3(TimerScreen, Screen):
    timer = NumericProperty(120)
    text_scenario = StringProperty("")
    scenarios = []
    current_scenario = None
    
    def __init__(self, **kwargs):
        super(Phase3, self).__init__(**kwargs)
        #Load the "scenarios" from my json file
        self.load_scenarios()
        
    def load_scenarios(self):
        try:
            with open("assets/scenarios.json", encoding='utf-8') as file:
                self.scenarios = json.load(file)
        except Exception as e:
            print(f"Falha ao carregar cenários: {e}")
            self.scenarios = []

    def on_enter(self):
        super(Phase3, self).on_enter()
        self.present_scenario()

    def present_scenario(self):
        if self.scenarios:
            self.current_scenario = choice(self.scenarios)
            self.text_scenario = self.current_scenario["scenario"]
            self.ids.consequences_label.text = ""

            decisions = self.current_scenario.get("decisions", [])
            for i, decision in enumerate(decisions, start=1):
                button_id = f"decision{i}"
                button = self.ids.get(button_id)
                if button:
                    button.text = decision["text"]
                    button.opacity = 1
                    button.disabled = False
                    button.on_release = lambda i=i: self.process_decision(i-1)
                else:
                    print(f"No button with id {button_id}")

            # Hide any unused buttons
            for i in range(len(decisions) + 1, 5):  # Assuming a max of 4 decisions
                button_id = f"decision{i}"
                button = self.ids.get(button_id)
                if button:
                    button.opacity = 0
                    button.disabled = True
                    button.text = ""

        else:
            self.text_scenario = "Erro ao carregar cenários"

    def process_decision(self, decision_index):
        decision = self.current_scenario["decisions"][decision_index]
        self.show_consequences(decision)

    
    def show_consequences(self, decision):
        text = decision["consequence"]
        success = decision["success"]

    # Atualiza o label com o texto da consequência
        self.ids.consequences_label.text = text
        
        if success:
            Clock.schedule_once(lambda dt: self.change_screen("winner_page"), 5)
        else:
            Clock.schedule_once(lambda dt: self.change_screen("lost_page"), 5)
        
    def change_screen(self, screen_name, *args):
        self.manager.current = screen_name


class LostPage(Screen):
    pass


class WonPage(Screen):
    pass


class ScreenManagement(ScreenManager):
    user_name = StringProperty('')


class CyberQuestApp(MDApp):
    def build(self):
        Window.size = (400, 700)
        Window.clearcolor = (0, 0, 0, 1)
        self.theme_cls.font_styles["Computer-Says-No"] = [
            "assets/font/computer-says-no.ttf",
            16
        ]
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Pink"
        sm = ScreenManager(transition=SwapTransition())
        sm.add_widget(Welcome(name="welcome_screen"))
        sm.add_widget(HomePage(name="homepage"))
        sm.add_widget(HowToPlay(name="how_to_play"))
        sm.add_widget(Phase1(name="phase1"))
        sm.add_widget(Phase2(name="phase2"))
        sm.add_widget(Phase3(name="phase3"))
        sm.add_widget(WonPage(name="winner_page"))
        sm.add_widget(LostPage(name="lost_page"))
        return sm

    def reset_game(self):
        self.root.get_screen("phase1").reset_timer(30)
        self.root.get_screen("phase2").reset_phase2()
        self.root.get_screen("phase3").reset_timer(120)

        self.root.current = "homepage"


if __name__ == "__main__":
    CyberQuestApp().run()
