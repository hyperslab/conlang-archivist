import sqlite3

DB_FILE_PATH = 'languages.db'

max_word_id = -1


def new_word_id():
    global max_word_id
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    res = cur.execute('SELECT MAX(word_id) FROM word')
    row = res.fetchone()
    con.close()
    if row is None:
        word_id = 0
    else:
        word_id, = row
        if word_id is None:
            word_id = 0
    max_word_id = max(max_word_id + 1, word_id + 1)
    return max_word_id
