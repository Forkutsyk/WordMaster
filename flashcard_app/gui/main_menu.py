from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from database.db_manager import DatabaseManager


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        layout = BoxLayout(orientation='vertical')
        self.counter = Label(text=self.update_counter())
        layout.add_widget(self.counter)

        buttons = [
            ("Add New Words", self.go_to_add_words),
            ("Learn Session", self.go_to_learn_session),
            ("Dictionary", self.go_to_dictionary)
        ]

        for text, callback in buttons:
            btn = Button(text=text)
            btn.bind(on_press=callback)
            layout.add_widget(btn)

        self.add_widget(layout)

    def update_counter(self):
        total = self.db.get_total_words()
        known = self.db.get_known_words_count()
        return f"Total Words: {total} | Known Words: {known}"

    def go_to_add_words(self, instance):
        self.manager.current = 'add_words'

    def go_to_learn_session(self, instance):
        self.manager.current = 'learn_session'

    def go_to_dictionary(self, instance):
        self.manager.current = 'dictionary'