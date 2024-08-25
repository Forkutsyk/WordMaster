from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from database.db_manager import DatabaseManager


class Dictionary(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        layout = BoxLayout(orientation='vertical')

        self.word_list = TextInput(readonly=True, multiline=True)
        layout.add_widget(self.word_list)

        buttons = [
            ("All Words", self.show_all_words),
            ("Known Words", self.show_known_words),
            ("Unknown Words", self.show_unknown_words)
        ]

        for text, callback in buttons:
            btn = Button(text=text)
            btn.bind(on_press=callback)
            layout.add_widget(btn)

        self.add_widget(layout)

    def show_all_words(self, instance):
        words = self.db.get_all_words()
        self.word_list.text = '\n'.join([word['word'] for word in words])

    def show_known_words(self, instance):
        words = self.db.get_known_words()
        self.word_list.text = '\n'.join([word['word'] for word in words])

    def show_unknown_words(self, instance):
        words = self.db.get_unknown_words()
        self.word_list.text = '\n'.join([word['word'] for word in words])