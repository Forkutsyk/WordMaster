import sqlite3


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('flashcards.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_dictionary (
                id INTEGER PRIMARY KEY,
                word TEXT UNIQUE,
                definition TEXT,
                translation TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS known_words (
                id INTEGER PRIMARY KEY,
                word_id INTEGER,
                FOREIGN KEY (word_id) REFERENCES user_dictionary (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS unknown_words (
                id INTEGER PRIMARY KEY,
                word_id INTEGER,
                FOREIGN KEY (word_id) REFERENCES user_dictionary (id)
            )
        ''')
        self.conn.commit()

    def add_word(self, word, known=False):
        self.cursor.execute('INSERT OR IGNORE INTO user_dictionary (word) VALUES (?)', (word,))
        word_id = self.cursor.lastrowid
        if known:
            self.cursor.execute('INSERT INTO known_words (word_id) VALUES (?)', (word_id,))
        else:
            self.cursor.execute('INSERT INTO unknown_words (word_id) VALUES (?)', (word_id,))
        self.conn.commit()

    def get_total_words(self):
        self.cursor.execute('SELECT COUNT(*) FROM user_dictionary')
        return self.cursor.fetchone()[0]

    def get_known_words_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM known_words')
        return self.cursor.fetchone()[0]

    def get_words_for_learning(self):
        self.cursor.execute('''
            SELECT ud.id, ud.word FROM user_dictionary ud
            LEFT JOIN known_words kw ON ud.id = kw.word_id
            LEFT JOIN unknown_words uw ON ud.id = uw.word_id
            ORDER BY CASE 
                WHEN uw.id IS NOT NULL THEN 1 
                WHEN kw.id IS NOT NULL THEN 2
                ELSE 3 
            END, RANDOM()
            LIMIT 15
        ''')
        return [{'id': row[0], 'word': row[1]} for row in self.cursor.fetchall()]

    def update_word_status(self, word_id, known):
        if known:
            self.cursor.execute('DELETE FROM unknown_words WHERE word_id = ?', (word_id,))
            self.cursor.execute('INSERT OR IGNORE INTO known_words (word_id) VALUES (?)', (word_id,))
        else:
            self.cursor.execute('DELETE FROM known_words WHERE word_id = ?', (word_id,))
            self.cursor.execute('INSERT OR IGNORE INTO unknown_words (word_id) VALUES (?)', (word_id,))
        self.conn.commit()

    def get_all_words(self):
        self.cursor.execute('SELECT id, word FROM user_dictionary')
        return [{'id': row[0], 'word': row[1]} for row in self.cursor.fetchall()]

    def get_known_words(self):
        self.cursor.execute('''
            SELECT ud.id, ud.word FROM user_dictionary ud
            JOIN known_words kw ON ud.id = kw.word_id
        ''')
        return [{'id': row[0], 'word': row[1]} for row in self.cursor.fetchall()]

    def get_unknown_words(self):
        self.cursor.execute('''
            SELECT ud.id, ud.word FROM user_dictionary ud
            JOIN unknown_words uw ON ud.id = uw.word_id
        ''')
        return [{'id': row[0], 'word': row[1]} for row in self.cursor.fetchall()]