from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from gui.main_menu import MainMenu
from gui.add_words import AddWords
from gui.learn_session import LearnSession
from gui.dictionary import Dictionary


class FlashcardApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='main_menu'))
        sm.add_widget(AddWords(name='add_words'))
        sm.add_widget(LearnSession(name='learn_session'))
        sm.add_widget(Dictionary(name='dictionary'))
        return sm


if __name__ == '__main__':
    FlashcardApp().run()
