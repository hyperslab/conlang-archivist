import copy
import sqlite3
from sound import Sound
from word import Word
from sound_change_rule import SoundChangeRule
from language import Language
from word_form_rule import WordFormRule
import os

DB_FILE_PATH = 'languages.db'
LOGGING_LEVEL = 2  # https://learn.microsoft.com/en-us/dotnet/api/microsoft.extensions.logging.loglevel

language_cache = {}
word_cache = {}
caching_on = False


def log(message, level=2):
    if LOGGING_LEVEL <= level:
        print(message)


def enable_cache():
    global caching_on
    global language_cache
    global word_cache
    caching_on = True
    language_cache = {}
    word_cache = {}


def disable_cache():
    global caching_on
    global language_cache
    global word_cache
    caching_on = False
    language_cache = {}
    word_cache = {}


def create_db():
    log('Entering create_db', 2)
    con = sqlite3.connect(DB_FILE_PATH)
    con.execute('CREATE TABLE sound(sound_id INTEGER PRIMARY KEY, orthographic_transcription, ipa_transcription, '
                'phonotactics_categories, description)')
    con.execute('CREATE TABLE syllable(syllable_id INTEGER PRIMARY KEY, word_id, ordering)')
    con.execute('CREATE TABLE syllable_sound(syllable_id INTEGER, sound_id INTEGER, ordering INTEGER, PRIMARY KEY('
                'syllable_id, sound_id, ordering))')
    con.execute('CREATE TABLE word(word_id INTEGER PRIMARY KEY, categories, language_id, original_language_stage, '
                'obsoleted_language_stage, source_word_id, source_word_language_stage, stem_word_id, word_form_name, '
                'stem_word_language_stage)')
    con.execute('CREATE TABLE sound_change_rule(sound_change_rule_id INTEGER PRIMARY KEY, condition, stage)')
    con.execute('CREATE TABLE sound_change_rule_sound(sound_change_rule_id INTEGER, sound_id INTEGER, ordering '
                'INTEGER, new_not_old INTEGER, PRIMARY KEY(sound_change_rule_id, sound_id, ordering, new_not_old))')
    con.execute('CREATE TABLE word_sound_change_rule(word_id INTEGER, sound_change_rule_id INTEGER, ordering, '
                'PRIMARY KEY(word_id, sound_change_rule_id))')
    con.execute('CREATE TABLE language(language_id INTEGER PRIMARY KEY, name, phonotactics, source_language_id, '
                'source_language_stage)')
    con.execute('CREATE TABLE language_sound(language_id INTEGER, sound_id INTEGER, frequency, generation_options,'
                'PRIMARY KEY(language_id, sound_id))')
    con.execute('CREATE TABLE language_sound_change_rule(language_id INTEGER, sound_change_rule_id INTEGER, ordering, '
                'PRIMARY KEY(language_id, sound_change_rule_id))')
    con.execute('CREATE TABLE word_definition(word_id INTEGER, language_stage INTEGER, definition, '
                'PRIMARY KEY(word_id, language_stage))')
    con.execute('CREATE TABLE sound_change_rule_condition_sound(sound_change_rule_id INTEGER, sound_id INTEGER, '
                'ordering INTEGER, PRIMARY KEY(sound_change_rule_id, sound_id, ordering))')
    con.execute('CREATE TABLE word_form_rule(word_form_rule_id INTEGER PRIMARY KEY, name, categories, language_id, '
                'original_language_stage, obsoleted_language_stage)')
    con.execute('CREATE TABLE word_form_rule_sound_change_rule(word_form_rule_id INTEGER, sound_change_rule_id '
                'INTEGER, ordering INTEGER, change_not_base INTEGER, PRIMARY KEY(word_form_rule_id, '
                'sound_change_rule_id, ordering, change_not_base))')
    con.close()
    log('Exiting create_db', 2)


def delete_db():
    log('Entering delete_db', 3)
    os.remove(DB_FILE_PATH)
    log('Exiting delete_db', 3)


def insert_sound(sound):
    log('Entering insert_sound', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur.execute('INSERT INTO sound(orthographic_transcription, ipa_transcription, phonotactics_categories, '
                'description) VALUES(?, ?, ?, ?)', (sound.orthographic_transcription,
                                                    sound.ipa_transcription,
                                                    sound.phonotactics_categories,
                                                    sound.description))
    sound_id = cur.lastrowid
    con.commit()
    sound.sound_id = sound_id
    con.close()
    log('Exiting insert_sound', 1)
    return sound_id


def safe_insert_sound(sound):
    log('Entering safe_insert_sound', 1)
    if sound is None:
        return None
    sound_id = None
    if sound.sound_id is not None:
        con = sqlite3.connect(DB_FILE_PATH)
        cur = con.cursor()
        for (row,) in cur.execute('SELECT sound_id FROM sound WHERE sound_id = ?', (sound.sound_id,)):
            sound_id = row
        con.close()
    if sound_id is None:
        log('Exiting safe_insert_sound after inserting', 1)
        return insert_sound(sound)
    else:
        log('Exiting safe_insert_sound without inserting', 1)
        return sound_id


def insert_syllable(word_id, ordering):
    log('Entering insert_syllable', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur.execute('INSERT INTO syllable(word_id, ordering) VALUES(?, ?)', (word_id, ordering))
    syllable_id = cur.lastrowid
    con.commit()
    con.close()
    log('Exiting insert_syllable', 1)
    return syllable_id


def insert_syllable_sound(syllable_id, sound_id, ordering):
    log('Entering insert_syllable_sound', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        with con:
            con.execute('INSERT INTO syllable_sound(syllable_id, sound_id, ordering) VALUES(?, ?, ?)', (syllable_id,
                                                                                                        sound_id,
                                                                                                        ordering))
    except sqlite3.IntegrityError as err:
        log('Error in insert_syllable_sound: ' + str(err), 4)
    con.close()
    log('Exiting insert_syllable_sound', 1)


def insert_word(word, language_id, insert_forms=True):
    log('Entering insert_word', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    if not word.word_id:
        word.word_id = get_new_word_id()
    cur.execute('INSERT INTO word(word_id, categories, language_id, original_language_stage, '
                'obsoleted_language_stage, source_word_id, source_word_language_stage, stem_word_id, word_form_name, '
                'stem_word_language_stage) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (word.word_id, word.categories, language_id, word.original_language_stage,
                 word.obsoleted_language_stage, word.source_word_id, word.source_word_language_stage, word.stem_word_id,
                 word.word_form_name, word.stem_word_language_stage))
    con.commit()
    if word.base_stem is not None:
        i = 0
        while i < len(word.base_stem):
            syllable_id = insert_syllable(word.word_id, i)
            j = 0
            while j < len(word.base_stem[i]):
                sound_id = safe_insert_sound(word.base_stem[i][j])
                insert_syllable_sound(syllable_id, sound_id, j)
                j = j + 1
            i = i + 1
    for language_sound_change in word.language_sound_changes:
        safe_insert_sound_change_rule(language_sound_change)
    i = 0
    for word_sound_change in word.word_sound_changes:
        sound_change_rule_id = safe_insert_sound_change_rule(word_sound_change)
        insert_word_sound_change_rule(word.word_id, sound_change_rule_id, i)
        i = i + 1
    definitions = []
    for definition, language_stage in word.get_definitions_and_stages():
        definitions.append((word.word_id, language_stage, definition))
    cur2.executemany('INSERT INTO word_definition(word_id, language_stage, definition) VALUES(?, ?, ?)',
                     definitions)
    con.commit()
    if insert_forms:
        for form_word in word.word_forms:
            form_word.stem_word_id = word.word_id
            insert_word(form_word, language_id, insert_forms=insert_forms)
    con.close()
    log('Exiting insert_word', 1)
    return word.word_id


def insert_sound_change_rule(sound_change_rule):
    log('Entering insert_sound_change_rule', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur.execute('INSERT INTO sound_change_rule(condition, stage) VALUES(?, ?)',
                (sound_change_rule.condition, sound_change_rule.stage))
    sound_change_rule_id = cur.lastrowid
    con.commit()
    i = 0
    while i < len(sound_change_rule.old_sounds):
        sound_id = safe_insert_sound(sound_change_rule.old_sounds[i])
        insert_sound_change_rule_sound(sound_change_rule_id, sound_id, i, new_not_old=False)
        i = i + 1
    if sound_change_rule.new_sounds is not None:
        i = 0
        while i < len(sound_change_rule.new_sounds):
            sound_id = safe_insert_sound(sound_change_rule.new_sounds[i])
            insert_sound_change_rule_sound(sound_change_rule_id, sound_id, i, new_not_old=True)
            i = i + 1
    else:
        insert_sound_change_rule_sound(sound_change_rule_id, None, 0, new_not_old=True)
    if sound_change_rule.condition_sounds is not None:
        i = 0
        while i < len(sound_change_rule.condition_sounds):
            sound_id = safe_insert_sound(sound_change_rule.condition_sounds[i])
            insert_sound_change_rule_condition_sound(sound_change_rule_id, sound_id, i)
            i = i + 1
    sound_change_rule.sound_change_rule_id = sound_change_rule_id
    con.close()
    log('Exiting insert_sound_change_rule', 1)
    return sound_change_rule_id


def safe_insert_sound_change_rule(sound_change_rule):
    log('Entering safe_insert_sound_change_rule', 1)
    if sound_change_rule is None:
        return None
    sound_change_rule_id = None
    if sound_change_rule.sound_change_rule_id is not None:
        con = sqlite3.connect(DB_FILE_PATH)
        cur = con.cursor()
        for (row,) in cur.execute('SELECT sound_change_rule_id FROM sound_change_rule WHERE sound_change_rule_id = ?',
                                  (sound_change_rule.sound_change_rule_id,)):
            sound_change_rule_id = row
        con.close()
    log('Exiting safe_insert_sound_change_rule', 1)
    if sound_change_rule_id is None:
        return insert_sound_change_rule(sound_change_rule)
    else:
        return sound_change_rule_id


def insert_sound_change_rule_sound(sound_change_rule_id, sound_id, ordering, new_not_old):
    log('Entering insert_sound_change_rule_sound', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        with con:
            con.execute('INSERT INTO sound_change_rule_sound(sound_change_rule_id, sound_id, ordering, new_not_old) '
                        'VALUES(?, ?, ?, ?)', (sound_change_rule_id, sound_id, ordering, new_not_old))
    except sqlite3.IntegrityError as err:
        log('Error in insert_sound_change_rule_sound: ' + str(err), 4)
    con.close()
    log('Exiting insert_sound_change_rule_sound', 1)


def insert_sound_change_rule_condition_sound(sound_change_rule_id, sound_id, ordering):
    log('Entering insert_sound_change_rule_condition_sound', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        with con:
            con.execute('INSERT INTO sound_change_rule_condition_sound(sound_change_rule_id, sound_id, ordering) '
                        'VALUES(?, ?, ?)', (sound_change_rule_id, sound_id, ordering))
    except sqlite3.IntegrityError as err:
        log('Error in insert_sound_change_rule_condition_sound: ' + str(err), 4)
    con.close()
    log('Exiting insert_sound_change_rule_condition_sound', 1)


def insert_word_sound_change_rule(word_id, sound_change_rule_id, ordering):
    log('Entering insert_word_sound_change_rule', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        with con:
            con.execute('INSERT INTO word_sound_change_rule(word_id, sound_change_rule_id, ordering) VALUES(?, ?, ?)',
                        (word_id, sound_change_rule_id, ordering))
    except sqlite3.IntegrityError as err:
        log('Error in insert_word_sound_change_rule for word_id ' + str(word_id) + ' and sound_change_rule_id ' +
            str(sound_change_rule_id) + ': ' + str(err), 4)
    con.close()
    log('Exiting insert_word_sound_change_rule', 1)


def insert_language(language):
    log('Entering insert_language', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    source_language_id = None
    if language.source_language is not None:
        source_language_id = language.source_language.language_id
    cur.execute('INSERT INTO language(name, phonotactics, source_language_id, source_language_stage) '
                'VALUES(?, ?, ?, ?)', (language.name, language.phonotactics, source_language_id,
                                       language.source_language_stage))
    language_id = cur.lastrowid
    con.commit()
    i = 0
    while i < len(language.original_phonetic_inventory):
        sound_id = safe_insert_sound(language.original_phonetic_inventory[i])
        insert_language_sound(language_id, language.original_phonetic_inventory[i])
        i = i + 1
    i = 0
    while i < len(language.words):
        insert_word(language.words[i], language_id)
        i = i + 1
    i = 0
    for sound_change in language.sound_changes:
        sound_change_rule_id = safe_insert_sound_change_rule(sound_change)
        insert_language_sound_change_rule(language_id, sound_change_rule_id, i)
        i = i + 1
    for word_form in language.word_forms:
        insert_word_form_rule(word_form, language_id)
    language.language_id = language_id
    con.close()
    log('Exiting insert_language', 1)
    return language_id


def insert_language_sound(language_id, sound):
    log('Entering insert_language_sound', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        with con:
            con.execute('INSERT INTO language_sound(language_id, sound_id, frequency, generation_options)'
                        'VALUES(?, ?, ?, ?)',
                        (language_id, sound.sound_id, sound.frequency, sound.get_generation_options()))
    except sqlite3.IntegrityError:
        pass
    con.close()
    log('Exiting insert_language_sound', 1)


def insert_language_sound_change_rule(language_id, sound_change_rule_id, ordering):
    log('Entering insert_language_sound_change_rule', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        with con:
            con.execute('INSERT INTO language_sound_change_rule(language_id, sound_change_rule_id, ordering) '
                        'VALUES(?, ?, ?)', (language_id, sound_change_rule_id, ordering))
    except sqlite3.IntegrityError as err:
        log('Error in insert_language_sound_change_rule: ' + str(err), 4)
    con.close()
    log('Exiting insert_language_sound_change_rule', 1)


def insert_word_definition(word_id, language_stage, definition):
    log('Entering insert_word_definition', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        with con:
            con.execute('INSERT INTO word_definition(word_id, language_stage, definition) '
                        'VALUES(?, ?, ?)', (word_id, language_stage, definition))
    except sqlite3.IntegrityError as err:
        log('Error in insert_word_definition: ' + str(err), 4)
    con.close()
    log('Exiting insert_word_definition', 1)


def override_insert_word_definition(word_id, language_stage, definition):
    log('Entering override_insert_word_definition', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    cur.execute('DELETE FROM word_definition WHERE word_id = ? AND language_stage = ?', (word_id, language_stage))
    con.commit()
    cur2.execute('INSERT INTO word_definition(word_id, language_stage, definition) VALUES(?, ?, ?)',
                 (word_id, language_stage, definition))
    con.commit()
    con.close()
    log('Exiting override_insert_word_definition', 1)


def insert_word_form_rule(word_form_rule, language_id):
    log('Entering insert_word_form_rule', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur.execute('INSERT INTO word_form_rule(name, categories, language_id, original_language_stage, '
                'obsoleted_language_stage) VALUES(?, ?, ?, ?, ?)',
                (word_form_rule.name, word_form_rule.categories, language_id, word_form_rule.original_language_stage,
                 word_form_rule.obsoleted_language_stage))
    word_form_rule_id = cur.lastrowid
    con.commit()
    i = 0
    while i < len(word_form_rule.base_form_rules):
        sound_change_rule_id = safe_insert_sound_change_rule(word_form_rule.base_form_rules[i])
        insert_word_form_rule_sound_change_rule(word_form_rule_id, sound_change_rule_id, i, change_not_base=False)
        i = i + 1
    i = 0
    while i < len(word_form_rule.sound_changes):
        sound_change_rule_id = safe_insert_sound_change_rule(word_form_rule.sound_changes[i])
        insert_word_form_rule_sound_change_rule(word_form_rule_id, sound_change_rule_id, i, change_not_base=True)
        i = i + 1
    word_form_rule.word_form_rule_id = word_form_rule_id
    con.close()
    log('Exiting insert_word_form_rule', 1)
    return word_form_rule_id


def insert_word_form_rule_sound_change_rule(word_form_rule_id, sound_change_rule_id, ordering, change_not_base):
    log('Entering insert_word_form_rule_sound_change_rule', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    try:
        with con:
            con.execute('INSERT INTO word_form_rule_sound_change_rule(word_form_rule_id, sound_change_rule_id, '
                        'ordering, change_not_base) VALUES(?, ?, ?, ?)', (word_form_rule_id, sound_change_rule_id,
                                                                          ordering, change_not_base))
    except sqlite3.IntegrityError as err:
        log('Error in insert_word_form_rule_sound_change_rule: ' + str(err), 4)
    con.close()
    log('Exiting insert_word_form_rule_sound_change_rule', 1)


def fetch_sound(sound_id):
    log('Entering fetch_sound', 1)
    if sound_id is None:
        return None
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    res = cur.execute('SELECT orthographic_transcription, ipa_transcription, phonotactics_categories, description '
                      'FROM sound WHERE sound_id = ?', (sound_id,))
    orthographic_transcription, ipa_transcription, phonotactics_categories, description = res.fetchone()
    sound = Sound(orthographic_transcription=orthographic_transcription, ipa_transcription=ipa_transcription,
                  phonotactics_categories=phonotactics_categories, description=description)
    sound.sound_id = sound_id
    con.close()
    log('Exiting fetch_sound', 1)
    return sound


def fetch_word(word_id, fetch_source_word_language=True, fetch_forms=True, fetch_stem_word_language=True):
    log('Entering fetch_word', 1)  # TODO can be optimized to use one select and not call fetch_sound
    if word_id is None:
        return None
    if caching_on and word_id in word_cache:
        return word_cache[word_id]
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    cur4 = con.cursor()
    cur5 = con.cursor()
    cur6 = con.cursor()
    cur7 = con.cursor()
    cur8 = con.cursor()
    res = cur.execute('SELECT categories, original_language_stage, obsoleted_language_stage, source_word_id, '
                      'source_word_language_stage, stem_word_id, word_form_name, stem_word_language_stage, language_id '
                      'FROM word WHERE word_id = ?',
                      (word_id,))
    categories, original_language_stage, obsoleted_language_stage, source_word_id, source_word_language_stage, \
        stem_word_id, word_form_name, stem_word_language_stage, language_id = res.fetchone()
    res = cur2.execute('SELECT syllable_sound.sound_id, syllable.ordering, syllable_sound.ordering FROM syllable '
                       'INNER JOIN syllable_sound ON syllable.syllable_id = syllable_sound.syllable_id WHERE '
                       'syllable.word_id = ?',
                       (word_id,))
    stem = list()
    for sound_id, i, j in res:
        while len(stem) < i + 1:
            stem.append(list())
        while len(stem[i]) < j + 1:
            stem[i].append(None)
        stem[i][j] = fetch_sound(sound_id)
        if sound_id is None:
            log('Warning in fetch_word: sound_id was None', 3)
    res = cur8.execute('SELECT sound_change_rule_id FROM language_sound_change_rule WHERE language_id = ? AND '
                       'ordering >= ? AND (ordering < ? OR ? = -1)',
                       (language_id, original_language_stage, obsoleted_language_stage, obsoleted_language_stage))
    language_sound_changes = []
    for sound_change_rule_id, in res:
        language_sound_changes.append(fetch_sound_change_rule(sound_change_rule_id))
    word = Word(stem, categories, original_language_stage, assign_id=False)
    word.word_id = word_id
    if caching_on:
        word_cache[word_id] = word
    word.language_sound_changes = language_sound_changes
    word.obsoleted_language_stage = obsoleted_language_stage
    word.word_form_name = word_form_name if word_form_name else None
    if source_word_id:
        word.source_word_id = source_word_id
        word.source_word_language_stage = source_word_language_stage
        if fetch_source_word_language:
            res = cur5.execute('SELECT language_id FROM word WHERE word_id = ?', (source_word_id,))
            source_language_id, = res.fetchone()
            log('Caching: ' + str(caching_on) + 'Present: ' + str(source_language_id in language_cache), 1)
            if caching_on and source_language_id in language_cache:  # TODO do this without cache without infinite loop
                word.source_word_language = fetch_language(source_language_id)
    if stem_word_id:
        word.stem_word_id = stem_word_id
        word.stem_word_language_stage = stem_word_language_stage
        if fetch_stem_word_language:
            res = cur7.execute('SELECT language_id FROM word WHERE word_id = ?', (stem_word_id,))
            stem_language_id, = res.fetchone()
            log('Caching: ' + str(caching_on) + 'Present: ' + str(stem_language_id in language_cache), 1)
            if caching_on and stem_language_id in language_cache:  # TODO do this without cache without infinite loop
                word.stem_word_language = fetch_language(stem_language_id)
    res = cur3.execute('SELECT sound_change_rule_id FROM word_sound_change_rule WHERE word_id = ?', (word_id,))
    for sound_change_rule_id, in res:
        word.word_sound_changes.append(fetch_sound_change_rule(sound_change_rule_id))
    res = cur4.execute('SELECT definition, language_stage FROM word_definition WHERE word_id = ?', (word_id,))
    for definition, language_stage in res:
        word.definitions[language_stage] = definition
    if fetch_forms:
        res = cur6.execute('SELECT word_id FROM word WHERE stem_word_id = ?', (word_id,))
        for (word_form_id,) in res:
            form_word = fetch_word(word_form_id, fetch_source_word_language=fetch_source_word_language,
                                   fetch_forms=fetch_forms)
            form_word.stem_word_id = word_id
            word.word_forms.append(form_word)
    con.close()
    log('Exiting fetch_word', 1)
    return word


def fetch_sound_change_rule(sound_change_rule_id):  # TODO can be optimized to use one select and not call fetch_sound
    log('Entering fetch_sound_change_rule', 1)
    if sound_change_rule_id is None:
        return None
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    res = cur.execute('SELECT condition, stage '
                      'FROM sound_change_rule WHERE sound_change_rule_id = ?', (sound_change_rule_id,))
    condition, stage = res.fetchone()
    if stage is not None:
        stage = int(stage)
    else:
        stage = -1
    res = cur2.execute('SELECT sound_id, ordering, new_not_old FROM sound_change_rule_sound WHERE '
                       'sound_change_rule_id = ? ORDER BY ordering ASC', (sound_change_rule_id,))
    old_sounds = list()
    new_sounds = list()
    for sound_id, ordering, new_not_old in res:
        sound = fetch_sound(sound_id)
        if new_not_old:
            new_sounds.append(sound)
        else:
            old_sounds.append(sound)
    res = cur3.execute('SELECT sound_id, ordering FROM sound_change_rule_condition_sound WHERE '
                       'sound_change_rule_id = ? ORDER BY ordering ASC', (sound_change_rule_id,))
    condition_sounds = list()
    for sound_id, ordering in res:
        condition_sounds.append(fetch_sound(sound_id))
    sound_change_rule = SoundChangeRule(old_sounds, new_sounds, condition=condition, stage=stage,
                                        condition_sounds=condition_sounds)
    sound_change_rule.sound_change_rule_id = sound_change_rule_id
    con.close()
    log('Exiting fetch_sound_change_rule', 1)
    return sound_change_rule


def fetch_language_by_name(name, fetch_source_language=True):  # TODO out of date from fetch_langauge
    log('Entering fetch_language_by_name', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    cur4 = con.cursor()
    res = cur.execute('SELECT language_id, phonotactics, source_language_id, source_language_stage FROM language '
                      'WHERE name = ?', (name,))
    language_id, phonotactics, source_language_id, source_language_stage = res.fetchone()
    res = cur2.execute('SELECT sound.sound_id, orthographic_transcription, ipa_transcription, phonotactics_categories, '
                       'frequency, description, generation_options FROM sound INNER JOIN language_sound '
                       'ON sound.sound_id = language_sound.sound_id WHERE language_id = ?',
                       (language_id,))  # TODO break into own function
    phonetic_inventory = list()
    for sound_id, orthographic_transcription, ipa_transcription, phonotactics_categories, frequency, description, \
            generation_options in res:
        sound = Sound(orthographic_transcription, ipa_transcription, phonotactics_categories, frequency, description)
        sound.sound_id = sound_id
        sound.set_generation_options(generation_options)
        phonetic_inventory.append(sound)
    language = Language(name, phonetic_inventory, phonotactics)
    language.language_id = language_id
    if source_language_id:
        language.source_language_stage = source_language_stage
        if fetch_source_language:
            language.source_language = fetch_language(source_language_id)
    res = cur3.execute('SELECT sound_change_rule_id, ordering FROM language_sound_change_rule WHERE '
                       'language_id = ? ORDER BY ordering ASC', (language_id,))
    for sound_change_rule_id, ordering in res:
        language.apply_sound_change(fetch_sound_change_rule(sound_change_rule_id))
    res = cur4.execute('SELECT word_id FROM word WHERE language_id = ?', (language_id,))
    for (word_id,) in res:
        word = fetch_word(word_id)
        language.add_word(word, language_stage=word.original_language_stage)
    con.close()
    log('Exiting fetch_language_by_name', 1)
    return language


def check_language_by_name(name):
    log('Entering check_language_by_name', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    language_id = None
    for (row,) in cur.execute('SELECT language_id FROM language WHERE name = ?', (name,)):
        language_id = row
    con.close()
    log('Exiting check_language_by_name', 1)
    return language_id is not None


def fetch_language(language_id, fetch_source_language=True, fetch_child_languages=True, override_cache=False):
    log('Entering fetch_language', 1)
    if caching_on and not override_cache and language_id in language_cache:
        return language_cache[language_id]
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    cur4 = con.cursor()
    cur5 = con.cursor()
    cur6 = con.cursor()
    res = cur.execute('SELECT name, phonotactics, source_language_id, source_language_stage FROM language '
                      'WHERE language_id = ?', (language_id,))
    name, phonotactics, source_language_id, source_language_stage = res.fetchone()
    res = cur2.execute('SELECT sound.sound_id, orthographic_transcription, ipa_transcription, phonotactics_categories, '
                       'frequency, description, generation_options FROM sound INNER JOIN language_sound '
                       'ON sound.sound_id = language_sound.sound_id WHERE language_id = ?',
                       (language_id,))  # TODO break into own function
    phonetic_inventory = list()
    for sound_id, orthographic_transcription, ipa_transcription, phonotactics_categories, frequency, description, \
            generation_options in res:
        sound = Sound(orthographic_transcription, ipa_transcription, phonotactics_categories, frequency, description)
        sound.sound_id = sound_id
        sound.set_generation_options(generation_options)
        phonetic_inventory.append(sound)
    language = Language(name, phonetic_inventory, phonotactics)
    language.language_id = language_id
    if caching_on:
        language_cache[language_id] = language
    res = cur3.execute('SELECT sound_change_rule_id, ordering FROM language_sound_change_rule WHERE '
                       'language_id = ? ORDER BY ordering ASC', (language_id,))
    for sound_change_rule_id, ordering in res:
        language.apply_sound_change(fetch_sound_change_rule(sound_change_rule_id))
    res = cur4.execute('SELECT word_id FROM word WHERE language_id = ? AND word_form_name IS NULL', (language_id,))
    for (word_id,) in res:
        word = fetch_word(word_id)
        language.words.append(word)
    if source_language_id:
        language.source_language_stage = source_language_stage
        if fetch_source_language:
            language.source_language = fetch_language(source_language_id, fetch_child_languages=fetch_child_languages)
    if fetch_child_languages:
        language.child_languages = []
        res = cur5.execute('SELECT language_id FROM language WHERE source_language_id = ?', (language_id,))
        for (child_language_id,) in res:
            language.child_languages.append(fetch_language(child_language_id,
                                                           fetch_source_language=fetch_source_language))
    res = cur6.execute('SELECT word_form_rule_id FROM word_form_rule WHERE language_id = ?', (language_id,))
    for (word_form_rule_id,) in res:
        word_form = fetch_word_form_rule(word_form_rule_id)
        language.word_forms.append(word_form)  # don't use add_word_form since we don't want to trigger logic
    con.close()
    log('Exiting fetch_language', 1)
    return language


def fetch_all_languages():
    log('Entering fetch_all_languages', 1)
    enable_cache()
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    res = cur.execute('SELECT language_id FROM language WHERE source_language_id IS NULL')
    languages = []
    for (language_id,) in res:
        languages.append(fetch_language(language_id, fetch_child_languages=False))
    current_layer_languages = copy.copy(languages)
    next_layer_languages = []
    while len(current_layer_languages) > 0:
        for language in current_layer_languages:
            res = cur2.execute('SELECT language_id FROM language WHERE source_language_id = ?', (language.language_id,))
            for (language_id,) in res:
                child_language = fetch_language(language_id, fetch_child_languages=False)
                language.child_languages.append(child_language)
                languages.insert(languages.index(language) + 1, child_language)
                next_layer_languages.append(child_language)
        current_layer_languages = next_layer_languages
        next_layer_languages = []
    con.close()
    log('Exiting fetch_all_languages', 1)
    return languages


def fetch_word_form_rule(word_form_rule_id):
    log('Entering fetch_word_form_rule', 1)
    if word_form_rule_id is None:
        return None
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    res = cur.execute('SELECT name, categories, original_language_stage, obsoleted_language_stage FROM word_form_rule '
                      'WHERE word_form_rule_id = ?', (word_form_rule_id,))
    name, categories, original_language_stage, obsoleted_language_stage = res.fetchone()
    res = cur2.execute('SELECT sound_change_rule_id, ordering, change_not_base FROM word_form_rule_sound_change_rule '
                       'WHERE word_form_rule_id = ? ORDER BY ordering ASC', (word_form_rule_id,))
    base_sound_change_rules = []
    change_sound_change_rules = []
    for sound_change_rule_id, ordering, change_not_base in res:
        sound_change_rule = fetch_sound_change_rule(sound_change_rule_id)
        if change_not_base:
            change_sound_change_rules.append(sound_change_rule)
        else:
            base_sound_change_rules.append(sound_change_rule)
    word_form_rule = WordFormRule(name, categories, original_language_stage)
    word_form_rule.word_form_rule_id = word_form_rule_id
    word_form_rule.obsoleted_language_stage = obsoleted_language_stage
    word_form_rule.base_form_rules = base_sound_change_rules
    word_form_rule.sound_changes = change_sound_change_rules
    con.close()
    log('Exiting fetch_word_form_rule', 1)
    return word_form_rule


def update_sound(sound):
    log('Entering update_sound', 1)
    if not sound.sound_id:
        log('Sound does not have an ID, cannot update', 4)
        return False
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur.execute('UPDATE sound SET orthographic_transcription = ?, ipa_transcription = ?, phonotactics_categories = ?, '
                'description = ? WHERE sound_id = ?', (sound.orthographic_transcription,
                                                       sound.ipa_transcription,
                                                       sound.phonotactics_categories,
                                                       sound.description,
                                                       sound.sound_id))
    con.commit()
    con.close()
    log('Exiting update_sound', 1)
    return True


def update_language_sound(language_id, sound):
    log('Entering update_language_sound', 1)
    if not sound.sound_id:
        log('Sound does not have an ID, cannot update', 4)
        return False
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur.execute('UPDATE language_sound SET frequency = ?, generation_options = ? '
                'WHERE language_id = ? AND sound_id = ?',
                (sound.frequency, sound.get_generation_options(), language_id, sound.sound_id))
    con.commit()
    con.close()
    log('Exiting update_language_sound', 1)
    return True


def update_word(word, refresh_sounds=True, refresh_definitions=True):
    log('Entering update_word', 1)
    if not word.word_id:
        log('Word does not have an ID, cannot update', 4)
        return False
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    cur4 = con.cursor()
    cur5 = con.cursor()
    cur.execute('UPDATE word SET categories = ?, original_language_stage = ?, obsoleted_language_stage = ? WHERE '
                'word_id = ?',
                (word.categories, word.original_language_stage, word.obsoleted_language_stage, word.word_id))
    con.commit()
    if refresh_sounds:
        cur2.execute('DELETE FROM syllable_sound WHERE syllable_id IN '
                     '(SELECT syllable_id FROM syllable WHERE word_id = ?)', (word.word_id,))
        cur3.execute('DELETE FROM syllable WHERE word_id = ?', (word.word_id,))
        con.commit()
        i = 0
        while i < len(word.base_stem):
            syllable_id = insert_syllable(word.word_id, i)
            j = 0
            while j < len(word.base_stem[i]):
                sound_id = safe_insert_sound(word.base_stem[i][j])
                insert_syllable_sound(syllable_id, sound_id, j)
                j = j + 1
            i = i + 1
    if refresh_definitions:
        cur4.execute('DELETE FROM word_definition WHERE word_id = ?', (word.word_id,))
        con.commit()
        definitions = []
        for definition, language_stage in word.get_definitions_and_stages():
            definitions.append((word.word_id, language_stage, definition))
        cur5.executemany('INSERT INTO word_definition(word_id, language_stage, definition) VALUES(?, ?, ?)',
                         definitions)
        con.commit()
    con.close()
    log('Exiting update_word', 1)
    return True


def update_language(language):
    log('Entering update_language', 1)
    if not language.language_id:
        log('Language does not have an ID, cannot update', 4)
        return False
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur.execute('UPDATE language SET name = ?, phonotactics = ? WHERE language_id = ?',
                (language.name, language.phonotactics, language.language_id))
    con.commit()
    con.close()
    log('Exiting update_language', 1)
    return True


def update_sound_change_rule(sound_change_rule, refresh_sounds=True):
    log('Entering update_sound_change_rule', 1)
    if not sound_change_rule.sound_change_rule_id:
        log('Sound change rule does not have an ID, cannot update', 4)
        return False
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    cur.execute('UPDATE sound_change_rule SET condition = ?, stage = ? WHERE sound_change_rule_id = ?',
                (sound_change_rule.condition, sound_change_rule.stage,
                 sound_change_rule.sound_change_rule_id))
    con.commit()
    if refresh_sounds:
        cur2.execute('DELETE FROM sound_change_rule_sound WHERE sound_change_rule_id = ? ',
                     (sound_change_rule.sound_change_rule_id,))
        con.commit()
        i = 0
        while i < len(sound_change_rule.old_sounds):
            sound_id = safe_insert_sound(sound_change_rule.old_sounds[i])
            insert_sound_change_rule_sound(sound_change_rule.sound_change_rule_id, sound_id, i, new_not_old=False)
            i = i + 1
        if sound_change_rule.new_sounds is not None:
            i = 0
            while i < len(sound_change_rule.new_sounds):
                sound_id = safe_insert_sound(sound_change_rule.new_sounds[i])
                insert_sound_change_rule_sound(sound_change_rule.sound_change_rule_id, sound_id, i, new_not_old=True)
                i = i + 1
        else:
            insert_sound_change_rule_sound(sound_change_rule.sound_change_rule_id, None, 0, new_not_old=True)
        if sound_change_rule.condition_sounds is not None:
            cur3.execute('DELETE FROM sound_change_rule_condition_sound WHERE sound_change_rule_id = ? ',
                         (sound_change_rule.sound_change_rule_id,))
            con.commit()
            i = 0
            while i < len(sound_change_rule.condition_sounds):
                sound_id = safe_insert_sound(sound_change_rule.condition_sounds[i])
                insert_sound_change_rule_condition_sound(sound_change_rule.sound_change_rule_id, sound_id, i)
                i = i + 1
    con.close()
    log('Exiting update_sound_change_rule', 1)
    return True


def update_word_form_rule(word_form_rule, refresh_sound_change_rules=True):
    log('Entering update_word_form_rule', 1)
    if not word_form_rule.word_form_rule_id:
        log('Word form rule does not have an ID, cannot update', 4)
        return False
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    cur.execute('UPDATE word_form_rule SET name = ?, categories = ?, original_language_stage = ?, '
                'obsoleted_language_stage = ? WHERE word_form_rule_id = ?',
                (word_form_rule.name, word_form_rule.categories, word_form_rule.original_language_stage,
                 word_form_rule.obsoleted_language_stage, word_form_rule.word_form_rule_id))
    con.commit()
    if refresh_sound_change_rules:
        cur2.execute('DELETE FROM word_form_rule_sound_change_rule WHERE word_form_rule_id = ? ',
                     (word_form_rule.word_form_rule_id,))
        con.commit()
        i = 0
        while i < len(word_form_rule.base_form_rules):
            sound_change_rule_id = safe_insert_sound_change_rule(word_form_rule.base_form_rules[i])
            insert_word_form_rule_sound_change_rule(word_form_rule.word_form_rule_id, sound_change_rule_id, i,
                                                    change_not_base=False)
            i = i + 1
        i = 0
        while i < len(word_form_rule.sound_changes):
            sound_change_rule_id = safe_insert_sound_change_rule(word_form_rule.sound_changes[i])
            insert_word_form_rule_sound_change_rule(word_form_rule.word_form_rule_id, sound_change_rule_id, i,
                                                    change_not_base=True)
            i = i + 1
    con.close()
    log('Exiting update_word_form_rule', 1)
    return True


def reload_language(language):  # TODO possibly out of date with fetch_langauge (merge the code somehow?)
    log('Entering reload_language', 1)
    language.sound_changes = []
    language.words = []
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    cur4 = con.cursor()
    res = cur.execute('SELECT name, phonotactics FROM language WHERE language_id = ?', (language.language_id,))
    name, phonotactics = res.fetchone()
    res = cur2.execute('SELECT sound.sound_id, orthographic_transcription, ipa_transcription, phonotactics_categories, '
                       'frequency, description, generation_options FROM sound INNER JOIN language_sound '
                       'ON sound.sound_id = language_sound.sound_id WHERE language_id = ?',
                       (language.language_id,))  # TODO break into own function
    language.name = name
    language.phonotactics = phonotactics
    phonetic_inventory = []
    for sound_id, orthographic_transcription, ipa_transcription, phonotactics_categories, frequency, description, \
            generation_options in res:
        sound = Sound(orthographic_transcription, ipa_transcription, phonotactics_categories, frequency, description)
        sound.sound_id = sound_id
        sound.set_generation_options(generation_options)
        phonetic_inventory.append(sound)
    language.original_phonetic_inventory = phonetic_inventory
    language.modern_phonetic_inventory = copy.copy(phonetic_inventory)
    res = cur3.execute('SELECT sound_change_rule_id, ordering FROM language_sound_change_rule WHERE '
                       'language_id = ? ORDER BY ordering ASC', (language.language_id,))
    for sound_change_rule_id, ordering in res:
        language.apply_sound_change(fetch_sound_change_rule(sound_change_rule_id))
    res = cur4.execute('SELECT word_id FROM word WHERE language_id = ? AND word_form_name IS NULL',
                       (language.language_id,))
    for (word_id,) in res:
        word = fetch_word(word_id)
        language.words.append(word)
    con.close()
    log('Exiting reload_language', 1)


def get_new_word_id():
    log('Entering get_new_word_id', 1)
    con = sqlite3.connect(DB_FILE_PATH)
    cur = con.cursor()
    res = cur.execute('SELECT MAX(word_id) FROM word')
    row = res.fetchone()
    con.close()
    if row is None:
        log('Exiting get_new_word_id', 1)
        return 1
    word_id, = row
    if word_id is None:
        log('Exiting get_new_word_id', 1)
        return 1
    word_id = int(word_id)
    log('Exiting get_new_word_id', 1)
    return word_id + 1
