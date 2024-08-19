import tkinter as tk
from tkinter import messagebox
import requests
import sqlite3

# Function to fetch a random word from an expanded word list
def fetch_word():
    print("Fetching a new word...")
    response = requests.get("https://random-word-api.herokuapp.com/word?number=1")
    words = response.json()
    if words:
        return words[0]
    return None

# Function to fetch the definition of a word from the Datamuse API
def fetch_definition(word):
    response = requests.get(f"https://api.datamuse.com/words?ml={word}&max=1")
    definitions = response.json()
    if definitions:
        return definitions[0]['word']
    return "Definition not found."

# Function to update the word display
def update_word():
    global current_word
    current_word = fetch_word()
    print(f"Updating word display to: {current_word}")
    word_label.config(text=current_word)

# Function to show the definition of the current word
def show_definition():
    definition = fetch_definition(current_word)
    messagebox.showinfo("Definition", f"{current_word}: {definition}")

# Function to save a word to the known_words table
def save_known_word(word):
    print(f"Saving known word: {word}")
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute("INSERT INTO known_words (word) VALUES (?)", (word,))
    conn.commit()
    conn.close()

# Function to save a word to the unknown_words table
def save_unknown_word(word):
    print(f"Saving unknown word: {word}")
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute("INSERT INTO unknown_words (word) VALUES (?)", (word,))
    conn.commit()
    conn.close()

# Function to handle the "I know" button click
def i_know():
    save_known_word(current_word)
    update_word()

# Function to handle the "I don't know" button click
def i_dont_know():
    save_unknown_word(current_word)
    update_word()

# Function to create a new window to display the known or unknown words
def display_words(words, title):
    new_window = tk.Toplevel(root)
    new_window.title(title)
    new_window.geometry("300x400")

    scrollbar = tk.Scrollbar(new_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(new_window, yscrollcommand=scrollbar.set, font=("Helvetica", 14))
    for word in words:
        listbox.insert(tk.END, word)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=listbox.yview)

# Function to view the words in the known_words table
def view_known_words():
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute("SELECT word FROM known_words")
    words = c.fetchall()
    conn.close()
    known_words = [word[0] for word in words]
    display_words(known_words, "Known Words")

# Function to view the words in the unknown_words table
def view_unknown_words():
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute("SELECT word FROM unknown_words")
    words = c.fetchall()
    conn.close()
    unknown_words = [word[0] for word in words]
    display_words(unknown_words, "Unknown Words")

# Set up the SQLite database
def setup_database():
    print("Setting up the database...")
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS known_words (word TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS unknown_words (word TEXT)''')
    conn.commit()
    conn.close()

# Initialize the main window
root = tk.Tk()
root.title("Word Learning App")
root.geometry("600x200")

# Set up the database
setup_database()

# Initialize the current word
current_word = fetch_word()

# Create and place the word label in the center
word_label = tk.Label(root, text=current_word, font=("Helvetica", 24))
word_label.pack(expand=True)

# Create and place the buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

i_know_button = tk.Button(button_frame, text="I know", command=i_know, font=("Helvetica", 14))
i_know_button.pack(side=tk.LEFT, padx=10)

definition_button = tk.Button(button_frame, text="Definition", command=show_definition, font=("Helvetica", 14))
definition_button.pack(side=tk.LEFT, padx=10)

i_dont_know_button = tk.Button(button_frame, text="I don't know", command=i_dont_know, font=("Helvetica", 14))
i_dont_know_button.pack(side=tk.LEFT, padx=10)

# Add buttons to view known and unknown words
view_known_button = tk.Button(root, text="View Known Words", command=view_known_words, font=("Helvetica", 14))
view_known_button.pack(side=tk.LEFT, padx=10, pady=5)

view_unknown_button = tk.Button(root, text="View Unknown Words", command=view_unknown_words, font=("Helvetica", 14))
view_unknown_button.pack(side=tk.LEFT, padx=10, pady=5)

# Create and place the exit button with red color
exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Helvetica", 14), bg="red", fg="white")
exit_button.pack(side=tk.RIGHT, padx=10, pady=5)

# Function to handle window close event
def on_closing():
    root.quit()

# Bind the window close event to the on_closing function
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the main event loop
root.mainloop()
