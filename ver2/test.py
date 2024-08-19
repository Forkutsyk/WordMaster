import sqlite3
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import requests


# Database setup
class Database:
    def __init__(self, db_name='language_app.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_database()

    def setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY,
                word TEXT UNIQUE,
                definition TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS known_words (
                id INTEGER PRIMARY KEY,
                word_id INTEGER,
                FOREIGN KEY (word_id) REFERENCES words (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS unknown_words (
                id INTEGER PRIMARY KEY,
                word_id INTEGER,
                FOREIGN KEY (word_id) REFERENCES words (id)
            )
        ''')
        self.conn.commit()

    def add_word(self, word, definition):
        self.cursor.execute('INSERT OR IGNORE INTO words (word, definition) VALUES (?, ?)', (word, definition))
        self.conn.commit()

    def get_random_word(self):
        self.cursor.execute('SELECT word FROM words ORDER BY RANDOM() LIMIT 1')
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_to_known(self, word):
        self.cursor.execute('SELECT id FROM words WHERE word = ?', (word,))
        result = self.cursor.fetchone()
        if result:
            word_id = result[0]
            self.cursor.execute('INSERT OR IGNORE INTO known_words (word_id) VALUES (?)', (word_id,))
            self.cursor.execute('DELETE FROM unknown_words WHERE word_id = ?', (word_id,))
            self.conn.commit()
        else:
            print(f"Word '{word}' not found in the database.")

    def add_to_unknown(self, word):
        self.cursor.execute('SELECT id FROM words WHERE word = ?', (word,))
        result = self.cursor.fetchone()
        if result:
            word_id = result[0]
            self.cursor.execute('INSERT OR IGNORE INTO unknown_words (word_id) VALUES (?)', (word_id,))
            self.conn.commit()
        else:
            print(f"Word '{word}' not found in the database.")

    def get_definition(self, word):
        self.cursor.execute('SELECT definition FROM words WHERE word = ?', (word,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_random_unknown_word(self):
        self.cursor.execute('''
            SELECT words.word FROM words
            JOIN unknown_words ON words.id = unknown_words.word_id
            ORDER BY RANDOM() LIMIT 1
        ''')
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_known_words(self):
        self.cursor.execute('''
            SELECT words.word FROM words
            JOIN known_words ON words.id = known_words.word_id
        ''')
        return [row[0] for row in self.cursor.fetchall()]

    def get_unknown_words(self):
        self.cursor.execute('''
            SELECT words.word FROM words
            JOIN unknown_words ON words.id = unknown_words.word_id
        ''')
        return [row[0] for row in self.cursor.fetchall()]


# Word Generator with API integration
class WordGenerator:
    def __init__(self, database):
        self.database = database

    def generate_word(self):
        response = requests.get("https://random-word-api.herokuapp.com/word")
        if response.status_code == 200:
            word = response.json()[0]
            definition = self.get_definition(word)
            self.database.add_word(word, definition)
            return word
        else:
            return self.database.get_random_word()

    def get_definition(self, word):
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                meanings = data[0].get('meanings', [])
                if meanings:
                    return meanings[0].get('definitions', [{}])[0].get('definition', 'No definition found.')

        return self.database.get_definition(word)

    def categorize_word(self, word, known):
        if known:
            self.database.add_to_known(word)
        else:
            self.database.add_to_unknown(word)


# Flashcard System
class FlashcardSystem:
    def __init__(self, database):
        self.database = database

    def get_flashcard(self):
        return self.database.get_random_unknown_word()

    def check_answer(self, word, user_answer):
        correct_answer = self.database.get_definition(word)
        return user_answer.lower() == correct_answer.lower()


# New Word Window
class NewWordWindow(tk.Toplevel):
    def __init__(self, parent, word_generator):
        super().__init__(parent)
        self.parent = parent
        self.word_generator = word_generator
        self.title("Add New Word")
        self.geometry("300x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.word = self.word_generator.generate_word()
        self.definition = self.word_generator.get_definition(self.word)

        self.create_widgets()

    def create_widgets(self):
        self.word_label = tk.Label(self, text=self.word, font=("Arial", 18))
        self.word_label.pack(pady=20)

        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=20)

        self.know_button = tk.Button(button_frame, text="I know", command=self.know_word)
        self.know_button.pack(side=tk.LEFT, padx=5)

        self.definition_button = tk.Button(button_frame, text="Definition", command=self.show_definition)
        self.definition_button.pack(side=tk.LEFT, padx=5)

        self.dont_know_button = tk.Button(button_frame, text="I don't know", command=self.dont_know_word)
        self.dont_know_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = tk.Button(self, text="X", command=self.on_closing)
        self.exit_button.place(relx=1.0, rely=0, anchor="ne")

    def know_word(self):
        self.word_generator.categorize_word(self.word, True)
        self.next_word()

    def dont_know_word(self):
        self.word_generator.categorize_word(self.word, False)
        self.next_word()

    def show_definition(self):
        messagebox.showinfo("Definition", self.definition)

    def next_word(self):
        self.word = self.word_generator.generate_word()
        self.definition = self.word_generator.get_definition(self.word)
        self.word_label.config(text=self.word)

    def on_closing(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()


# GUI Application
class LanguageLearningApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Language Learning App")
        self.geometry("400x300")

        self.database = Database()
        self.word_generator = WordGenerator(self.database)
        self.flashcard_system = FlashcardSystem(self.database)

        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self, text="Welcome to Language Learning App!", font=("Arial", 14))
        self.label.pack(pady=20)

        self.add_word_button = tk.Button(self, text="Add New Word", command=self.open_new_word_window)
        self.add_word_button.pack(pady=10)

        self.learn_words_button = tk.Button(self, text="Learn Words", command=self.learn_words)
        self.learn_words_button.pack(pady=10)

        self.lookup_words_button = tk.Button(self, text="Lookup Words", command=self.lookup_words)
        self.lookup_words_button.pack(pady=10)

        self.quit_button = tk.Button(self, text="Quit", command=self.quit)
        self.quit_button.pack(pady=10)

    def open_new_word_window(self):
        NewWordWindow(self, self.word_generator)

    def learn_words(self):
        while True:
            word = self.flashcard_system.get_flashcard()
            if not word:
                messagebox.showinfo("Learning Complete", "No more words to learn. Add some new words!")
                break

            user_answer = simpledialog.askstring("Flashcard", f"What's the definition of '{word}'?")
            if user_answer is None:  # User clicked cancel
                break

            correct_answer = self.database.get_definition(word)
            if self.flashcard_system.check_answer(word, user_answer):
                messagebox.showinfo("Correct!", "Your answer is correct!")
            else:
                messagebox.showinfo("Incorrect", f"The correct definition is:\n\n{correct_answer}")

            if not messagebox.askyesno("Continue", "Do you want to continue learning?"):
                break

    def lookup_words(self):
        LookupWindow(self, self.database)


class LookupWindow(tk.Toplevel):
    def __init__(self, parent, database):
        super().__init__(parent)
        self.parent = parent
        self.database = database
        self.title("Lookup Words")
        self.geometry("400x300")

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        known_frame = ttk.Frame(self.notebook)
        unknown_frame = ttk.Frame(self.notebook)

        self.notebook.add(known_frame, text="Known Words")
        self.notebook.add(unknown_frame, text="Unknown Words")

        known_words = self.database.get_known_words()
        unknown_words = self.database.get_unknown_words()

        self.create_word_list(known_frame, known_words)
        self.create_word_list(unknown_frame, unknown_words)

    def create_word_list(self, parent, words):
        listbox = tk.Listbox(parent)
        listbox.pack(expand=True, fill="both")

        for word in words:
            listbox.insert(tk.END, word)

        def show_definition(event):
            selection = event.widget.curselection()
            if selection:
                word = event.widget.get(selection[0])
                definition = self.database.get_definition(word)
                messagebox.showinfo("Definition", f"Word: {word}\n\nDefinition: {definition}")

        listbox.bind('<Double-1>', show_definition)


if __name__ == "__main__":
    app = LanguageLearningApp()
    app.mainloop()
