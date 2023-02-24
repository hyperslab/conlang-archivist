import sqlite3
import platformdirs
import configparser
import os

# TODO need to figure out the import spaghetti so this doesn't have to be duplicated from db
CONFIG_DIRECTORY = platformdirs.user_config_dir('ConlangArchivist', appauthor=False, roaming=True)
if not os.path.exists(CONFIG_DIRECTORY):
    os.makedirs(CONFIG_DIRECTORY)
CONFIG_FILE_PATH = os.path.join(CONFIG_DIRECTORY, 'config.ini')
if not os.path.isfile(CONFIG_FILE_PATH):
    DB_DIRECTORY = platformdirs.user_data_dir('ConlangArchivist', appauthor=False, roaming=True)  # default
    config = configparser.ConfigParser()
    config['Database'] = {}
    config['Database']['Directory'] = DB_DIRECTORY
    with open(CONFIG_FILE_PATH, 'w') as configfile:
        config.write(configfile)
else:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    DB_DIRECTORY = config['Database']['Directory']
DB_FILE_PATH = os.path.join(DB_DIRECTORY, 'languages.db')

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
