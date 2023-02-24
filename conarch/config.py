import os
import configparser
import platformdirs

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
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
