from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
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


class HomePage(Screen):
    pass


class HowToPlay(Screen):
    pass


# temporizer
class TimerScreen(Screen):
    timer = NumericProperty(0)

    def on_enter(self):
        Clock.schedule_interval(self.update_timer, 1)

    def on_pre_leave(self):
        Clock.unschedule(self.update_timer)

    def reset_timer(self, initial_time):
        self.timer = initial_time

    def update_timer(self, dt):
        self.timer -= 1
        if self.timer == 0:
            self.manager.current = "lost_page"


class Phase1(TimerScreen, Screen):
    timer = NumericProperty(30)

# simplified method to verify answers
    def check_answer(self, selected_answer):
        if selected_answer == "correct":
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
    timer = NumericProperty(120)
    shift = NumericProperty(0)
    encrypted_message = StringProperty("")
    original_message = StringProperty("")
    info_label = StringProperty("")
    input_text = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_text = MDTextField(
            hint_text="Type your encrypted message here",
            multiline=False,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            on_text_validate=self.check_encryption,
        )

    def on_enter(self):
        Clock.schedule_interval(self.update_timer, 1)
        self.generate_encrypted_message()

# resets timer and user's input
    def reset_phase2(self):
        self.reset_timer(120)
        self.input_text = ""

    def generate_encrypted_message(self):
        self.original_message = "Mantenha suas senhas seguras e atualizadas"
        self.shift = random.randint(1, 25)
        self.encrypted_message = encrypt_message(self.original_message, self.shift)

        self.info_label = f"Shift: {self.shift}\nEncripte essa mensagem:\n {self.original_message}"

    # compares input text with original message
    def check_encryption(self, instance):
        input_text = instance.text.strip()
        if input_text == self.encrypted_message:
            self.manager.current = "phase3"
        else:
            self.manager.current = "lost_page"


class Phase3(TimerScreen, Screen):
    timer = NumericProperty(120)
    text_scenario = StringProperty("")

    def on_enter(self):
        Clock.schedule_interval(self.update_timer, 1)
        self.present_scenario()

    def change_screen(self, screen_name, *args):
        self.manager.current = screen_name

    def present_scenario(self):
        text_scenario = (
        "Você está rastreando um ataque em andamento."
        "Um grupo de hackers conhecido como 'DarkBit' está tentando infiltrar um servidor governamental com dados de 5 milhões de cidadões."
        "Eles obtiveram acesso a informações classificadas e deixaram pistas."
        "Sua missão é rastrear o invasor e evitar danos adicionais.\n\n"
    
        "Informações:\n"
        "- Alvo: Servidor governamental\n"
        "- Método de Invasão: Ameaça Persistente Avançada (APT)\n"
        "- Pistas: Mensagens cifradas nos registros do sistema"
)

        self.text_scenario = text_scenario

    def make_decision(self, decision_number):
        consequences_text = ""
        success = False

        if decision_number == 1:
            success = True
            consequences_text = "Você analisa meticulosamente os registros do sistema e decifra com sucesso as mensagens cifradas.\n"
            "Você descobre o plano do hacker e evita uma grande violação de dados.\n"
            "Parabéns! Você tomou a decisão certa."
        elif decision_number == 2:
            consequences_text = "Você inicia um contra-ataque, mas o hacker o supera e retaliando com um ataque mais forte.\n"
            "Infelizmente, o contra-ataque acaba falhando, resultando em mais danos.\n"
            "Você perdeu esta rodada. Boa sorte na próxima vez."
        elif decision_number == 3:
            success = True
            consequences_text = "Você colabora com especialistas externos em cibersegurança que fornecem insights valiosos e assistência.\n"
            "Juntos, vocês conseguem frustrar as tentativas do hacker e garantir a segurança do servidor.\n"
            "Parabéns! Você tomou a decisão certa."
        elif decision_number == 4:
            consequences_text = "Você decide desconectar o servidor para conter a violação, mas isso resulta em perda de dados e tempo de inatividade.\n"
            "O hacker aproveita a interrupção e escapa com informações sensíveis.\n"
            "Você perdeu esta rodada. Boa sorte na próxima vez."

        self.show_consequences(consequences_text, success)

    def show_consequences(self, text, success):
        consequences_label = MDLabel(text=text, font_size="18sp", halign="center", pos_hint={"center_x": 0.5, "center_y": 0.48}, markup=True, padding=5)

        self.add_widget(consequences_label)

        if success:
            Clock.schedule_once(functools.partial(self.change_screen, "winner_page"), 3)
        else:
            Clock.schedule_once(functools.partial(self.change_screen, "lost_page"), 3)


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

    def reset_game(self):
        self.root.get_screen("phase1").reset_timer(30)
        self.root.get_screen("phase2").reset_phase2()
        self.root.get_screen("phase3").reset_timer(120)

        self.root.current = "homepage"


if __name__ == "__main__":
    CyberEscapeApp().run()
