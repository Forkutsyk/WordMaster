from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database.db_manager import DatabaseManager
from api.dictionary_api import DictionaryAPI


class AddWords(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.api = DictionaryAPI()
        layout = BoxLayout(orientation='vertical')

        self.word_input = TextInput(hint_text='Enter a word')
        layout.add_widget(self.word_input)

        buttons = [
            ("I Know", self.mark_known),
            ("I Don't Know", self.mark_unknown),
            ("Get Definition", self.get_definition)
        ]

        for text, callback in buttons:
            btn = Button(text=text)
            btn.bind(on_press=callback)
            layout.add_widget(btn)

        self.add_widget(layout)

    def mark_known(self, instance):
        word = self.word_input.text
        self.db.add_word(word, known=True)
        self.word_input.text = ''

    def mark_unknown(self, instance):
        word = self.word_input.text
        self.db.add_word(word, known=False)
        self.word_input.text = ''

    def get_definition(self, instance):
        word = self.word_input.text
        definition = self.api.get_definition(word)
        popup = Popup(title=word, content=Label(text=definition), size_hint=(None, None), size=(400, 400))
        popup.open()