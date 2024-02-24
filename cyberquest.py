from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty
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
    current_round = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.asked_questions = []
        
    def on_enter(self, *args):
        super().on_enter(*args)
        self.current_round = 1
        self.load_question()

    def load_question(self, *args):
        if self.current_round > 4:
            self.manager.current = "phase2"
            return
        with open('assets/questions_db.json', 'r', encoding='utf-8') as f:
            questions_pool = json.load(f)["questions"]
            questions = [q for q in questions_pool if q["question"] not in self.asked_questions]
            if not questions:
                self.asked_questions = []
                questions = questions_pool
            selected_question = random.choice(questions)
            self.question = selected_question["question"]
            self.options = selected_question["options"]
            self.correct_index = selected_question["correct"]
            self.asked_questions.append(self.question)
        
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
            self.manager.score += 50
            if self.current_round < 4:
                self.current_round += 1
                self.load_question()
            else:
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
            self.manager.score += 300
            self.manager.current = "phase3"
        else:
            self.manager.current = "lost_page"


class Phase3(TimerScreen, Screen):
    timer = NumericProperty(120)
    text_scenario = StringProperty("")
    scenarios = ListProperty()
    current_scenario = None
    used_scenarios = ListProperty()
    
    def __init__(self, **kwargs):
        super(Phase3, self).__init__(**kwargs)
        self.load_scenarios()
        self.used_scenarios = []
        
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
            self.current_scenario = self.scenarios.pop(random.randint(0, len(self.scenarios) - 1))
            self.used_scenarios.append(self.current_scenario)
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

            for i in range(len(decisions) + 1, 5):
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

        self.ids.consequences_label.text = text
        
        if success:
            self.manager.score += 200
            Clock.schedule_once(lambda dt: self.change_screen("phase4"), 5)
        else:
            Clock.schedule_once(lambda dt: self.change_screen("lost_page"), 5)
        
    def change_screen(self, screen_name, *args):
        self.manager.current = screen_name
        

class Phase4(TimerScreen, Screen):
    timer = NumericProperty(90)
    messages = ListProperty([])
    used_messages = ListProperty()
    current_message = ObjectProperty()
    total_rounds = 4
    rounds_completed = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_messages()
        self.used_messages = []

    def load_messages(self):
        try:
            with open("assets/phishing_messages.json", encoding='utf-8') as file:
                self.messages = json.load(file)["messages"]
        except Exception as e:
            print(f"Erro ao carregar mensagens: {e}")
            self.messages = []

    def on_enter(self):
        super().on_enter()
        self.rounds_completed = 0
        self.present_random_message()

    def present_random_message(self):
        if self.rounds_completed < self.total_rounds and self.messages:
            self.current_message = random.choice(self.messages)
            self.messages.remove(self.current_message)
            self.ids.message_label.text = self.current_message["content"]
        else:
            self.manager.current = "winner_page"


    def process_choice(self, choice):
        self.rounds_completed += 1
        if self.rounds_completed < self.total_rounds:
            self.present_random_message()
        else:
            self.manager.current = "winner_page"
            self.manager.score += 100

class LostPage(Screen):
    def on_enter(self, *args):
        super().on_enter(*args)
        self.ids.score_label.text = f"Pontuação: {self.manager.score}"
    
    def play_again(self):
        app = MDApp.get_running_app()
        app.reset_game()


class WonPage(Screen):
    def on_enter(self, *args):
        super().on_enter(*args)
        self.ids.score_label.text = f"Pontuação: {self.manager.score}"
    
    def play_again(self):
        app = MDApp.get_running_app()
        app.reset_game()


class ScreenManagement(ScreenManager):
    user_name = StringProperty('')
    score = NumericProperty(0)
    asked_questions = ListProperty([])


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
        sm = ScreenManagement(transition=SwapTransition())
        sm.add_widget(Welcome(name="welcome_screen"))
        sm.add_widget(HomePage(name="homepage"))
        sm.add_widget(HowToPlay(name="how_to_play"))
        sm.add_widget(Phase1(name="phase1"))
        sm.add_widget(Phase2(name="phase2"))
        sm.add_widget(Phase3(name="phase3"))
        sm.add_widget(Phase4(name="phase4"))
        sm.add_widget(WonPage(name="winner_page"))
        sm.add_widget(LostPage(name="lost_page"))
        return sm

    def reset_game(self):
        phase1_screen = self.root.get_screen("phase1")
        phase1_screen.reset_timer(30)
        phase1_screen.round = 1
        self.root.get_screen("phase2").reset_phase2()
        self.root.get_screen("phase3").reset_timer(120)
        self.root.get_screen("phase4").reset_timer(90)
        phase4_screen = self.root.get_screen("phase4")
        phase4_screen.load_messages()
        phase4_screen.rounds_completed = 0
        self.root.score = 0
        self.root.current = "homepage"


if __name__ == "__main__":
    CyberQuestApp().run()
