from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from database.db_manager import DatabaseManager


class LearnSession(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.words = []
        self.current_index = 0
        layout = BoxLayout(orientation='vertical')

        self.word_label = Label(text='')
        layout.add_widget(self.word_label)

        buttons = [
            ("I Know", self.mark_known),
            ("I Don't Know", self.mark_unknown)
        ]

        for text, callback in buttons:
            btn = Button(text=text)
            btn.bind(on_press=callback)
            layout.add_widget(btn)

        self.add_widget(layout)

    def on_enter(self):
        self.words = self.db.get_words_for_learning()
        self.show_next_word()

    def show_next_word(self):
        if self.current_index < len(self.words):
            self.word_label.text = self.words[self.current_index]['word']
        else:
            self.word_label.text = "Learning session completed!"

    def mark_known(self, instance):
        if self.current_index < len(self.words):
            self.db.update_word_status(self.words[self.current_index]['id'], known=True)
        self.current_index += 1
        self.show_next_word()

    def mark_unknown(self, instance):
        if self.current_index < len(self.words):
            self.words.append(self.words[self.current_index])
        self.current_index += 1
        self.show_next_word()