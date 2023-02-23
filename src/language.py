import copy
from src.word import Word
import random


class Language:
    """One language. Contains sounds, words, and historical sound changes.

    A Language will keep track of its "original" form as well as all steps
    it took to evolve into its "modern" form. As such, each historical
    sound change (represented by a Sound Change Rule) that takes place in
    the language corresponds to one "stage" with the original form being
    represented by "stage" 0. In other words, a Language is divided into
    stages by its historical sound changes.

    All words, sounds, and word forms in a Language can be traced to being
    added either at stage 0, meaning they were always in the language, or
    at some later stage, which means they will not appear in earlier forms
    of the language. Words and word forms can also be "obsoleted" at a
    certain stage, meaning they will not appear from that stage onward.

    In general, all operations on a Language can be performed at any
    specified stage (if no stage is provided, the most recent stage is
    usually assumed). This means that a Language can be edited from any
    point in its history and the changes that apply will propagate to all
    future stages. The one exception to this (at the moment) is that
    historical sound changes cannot be inserted except at the most current
    language stage.
    """

    def __init__(self, name, phonetic_inventory, phonotactics):
        self.language_id = None
        self.name = name
        self.original_phonetic_inventory = phonetic_inventory
        self.phonotactics = phonotactics
        self.words = list()
        self.sound_changes = list()
        self.modern_phonetic_inventory = copy.copy(self.original_phonetic_inventory)
        self.source_language = None
        self.source_language_stage = None
        self.child_languages = list()
        self.word_forms = list()

    def add_word(self, word, language_stage=-1):
        if language_stage < 0:
            language_stage = self.get_current_stage()
        self.words.append(word)  # add word
        word.original_language_stage = language_stage

        # add language sound changes to word
        for sound_change in self.sound_changes:  # evolve words
            word.add_language_sound_change(sound_change)

        # add forms to word
        for word_form in self.get_forms_at_stage(language_stage):  # preexisting forms
            if any(category in word.categories for category in word_form.categories):
                self.apply_form_to_word(word_form, word)
        i = language_stage
        while i < len(self.sound_changes):
            i = i + 1
            if not word.word_form_name:  # add forms from the new language stage to word
                for word_form in self.get_forms_added_at_stage(i):
                    if any(category in word.categories for category in word_form.categories):
                        self.apply_form_to_word(word_form, word)

        # reassess phonetic inventory
        for syllable in word.get_modern_stem():
            for sound in syllable:
                if sound not in self.modern_phonetic_inventory:
                    self.modern_phonetic_inventory.append(sound)

    def add_words(self, words, language_stage=-1):
        for word in words:
            self.add_word(word, language_stage)

    def generate_word(self, min_syllable_length=1, max_syllable_length=2, category='', language_stage=-1,
                      assign_id=True):
        return self.generate_words(1, min_syllable_length, max_syllable_length, category=category,
                                   language_stage=language_stage, assign_ids=assign_id)[0]

    def generate_words(self, words=1, min_syllable_length=1, max_syllable_length=2, category='', language_stage=-1,
                       assign_ids=True):
        new_words = list()
        for i in range(words):
            stem = list()
            syllable_range = range(0, random.randint(min_syllable_length, max_syllable_length))
            previous_syllable = None
            for j in syllable_range:
                previous_syllable = self.generate_syllable(language_stage=language_stage, word_initial=j == 0,
                                                           word_final=j == len(syllable_range) - 1,
                                                           previous_syllable=previous_syllable)
                stem.append(previous_syllable)
            new_words.append(Word(stem, category, assign_id=assign_ids))
        return new_words

    def generate_syllable(self, phonotactics=None, language_stage=-1, word_initial=False, word_final=False,
                          ignore_generation_options=False, previous_syllable=None):
        if phonotactics is None:
            tactics = self.phonotactics
        else:
            tactics = phonotactics

        # Step 1: resolve parentheses in phonotactics string
        i = 0
        new_tactics = ''
        while i < len(tactics):
            if tactics[i] != '(':
                if tactics[i] != ')':
                    new_tactics = new_tactics + tactics[i]
            else:
                chance = 0.5
                if i + 1 < len(tactics) and tactics[i + 1] in '123456789':  # pull chance from tactics, if provided
                    i = i + 1
                    chance = float(tactics[i]) / 10.0
                if random.random() < chance:  # add the sounds in parentheses
                    pass
                else:  # ignore the sounds in parentheses
                    while tactics[i] != ')':
                        i = i + 1
            i = i + 1
        tactics = new_tactics

        # Step 2: resolve braces in phonotactics string
        i = 0
        new_tactics = ''
        while i < len(tactics):
            if tactics[i] != '{':
                new_tactics = new_tactics + tactics[i]
            else:
                possible_sounds = list()
                while tactics[i] != '}':
                    i = i + 1
                    assert i < len(tactics)
                    if tactics[i] not in ', ;/|123456789{}':
                        possible_sounds.append(tactics[i])
                new_tactics = new_tactics + random.choice(possible_sounds)
            i = i + 1
        tactics = new_tactics

        # Step 3: determine phonetic inventory based on language stage
        if language_stage < 0 or language_stage >= self.get_current_stage():
            phonetic_inventory = self.modern_phonetic_inventory
        elif language_stage == 0:
            phonetic_inventory = self.original_phonetic_inventory
        else:
            phonetic_inventory = self.get_phonetic_inventory_at_stage(language_stage)

        # Step 4: pick a sound for each category in the processed phonotactics string
        syllable = list()
        i = 0
        while i < len(tactics):
            possible_sounds = [s for s in phonetic_inventory if tactics[i] in s.phonotactics_categories
                               and (ignore_generation_options or
                                    s.allowed_by_generation_options(tactics, syllable,
                                                                    word_initial_syllable=word_initial,
                                                                    word_final_syllable=word_final,
                                                                    previous_syllable=previous_syllable))]
            if len(possible_sounds) > 0:
                syllable.append(random.choices([s for s in possible_sounds],
                                               weights=[s.frequency for s in possible_sounds])[0])
            i += 1
        return syllable

    def apply_sound_change(self, sound_change):
        self.sound_changes.append(sound_change)
        for word in self.words:
            word.add_language_sound_change(sound_change)
        if not sound_change.condition and len(sound_change.old_sounds) == 1:
            if sound_change.old_sounds[0] in self.modern_phonetic_inventory:
                self.modern_phonetic_inventory.remove(sound_change.old_sounds[0])
        if sound_change.new_sounds is not None:
            for sound in sound_change.new_sounds:
                if sound not in self.modern_phonetic_inventory:
                    self.modern_phonetic_inventory.append(sound)

    def add_word_form(self, word_form, use_current_stage=True):
        if use_current_stage:
            word_form.original_language_stage = self.get_current_stage()
        self.word_forms.append(word_form)
        for word in self.copy_words_at_stage(word_form.original_language_stage, include_all_definitions=True):
            if any(category in word.categories for category in word_form.categories):
                self.apply_form_to_word(word_form, word, word.copied_from)

    def apply_form_to_word(self, word_form, word, original_word=None):
        if original_word is None:  # if you're applying to a copy, this is the original
            original_word = word
        form_word = Word(None, word.categories, max(word_form.original_language_stage, word.original_language_stage))
        form_word.word_form_name = word_form.name
        if word.obsoleted_language_stage > -1 < word_form.obsoleted_language_stage:
            form_word.obsoleted_language_stage = min(word.obsoleted_language_stage,
                                                     word_form.obsoleted_language_stage)
        else:  # little trick to use whichever is not -1, or -1 if they both are, since it will never be < -1
            form_word.obsoleted_language_stage = max(word.obsoleted_language_stage,
                                                     word_form.obsoleted_language_stage)
        for stage, definition in word.definitions.items():
            form_word.add_definition(word_form.name + ' form of a word meaning: ' + definition, stage)
        form_word.language_sound_changes = copy.copy(word.language_sound_changes)
        form_word.word_sound_changes = copy.copy(word.word_sound_changes)
        for conjugation_rule in word_form.get_adjusted_rules():  # forms have a None base stem and are calculated on the
            form_word.add_word_sound_change(conjugation_rule)    # fly; this is where the rules live
        form_word.stem_word_id = original_word.word_id           # and this is what the rules apply to
        form_word.stem_word_language = self
        form_word.stem_word_language_stage = max(word_form.original_language_stage, word.original_language_stage)
        original_word.word_forms.append(form_word)

    def print_all_word_forms(self, include_ipa=False, include_base_stem=False):
        for word in self.words:
            divider_length = word.print_all_forms(include_ipa=include_ipa, include_base_stem=include_base_stem)
            print('-' * divider_length)

    def get_full_sound_inventory(self):
        sounds = set()
        for i in range(0, self.get_current_stage() + 1):
            for sound in self.get_phonetic_inventory_at_stage(i):
                sounds.add(sound)
        return list(sounds)

    def get_current_stage(self):
        return len(self.sound_changes)

    def copy_words_at_stage(self, language_stage=-1, include_previous_stages=True, include_language_sound_changes=True,
                            branch=False, include_all_definitions=False, preserve_ids=False):
        """Return a list containing copies of all words that existed at a certain language stage.

        The words will exist as they did at the specified stage, including all language sound changes and word sound
        changes up to and including the specified stage, and none from future stages.
        """

        if language_stage < 0:
            language_stage = self.get_current_stage()
        stage_words = list()

        # determine which words to include
        for word in self.words:
            if include_previous_stages:
                if word.original_language_stage <= language_stage:
                    new_word = copy.copy(word)
                    if not preserve_ids:
                        new_word.word_id = None
                    if branch:
                        new_word.set_as_branch(word, self, language_stage)
                    new_word.copied_from = word
                    stage_words.append(new_word)
            else:
                if word.original_language_stage == language_stage:
                    new_word = copy.copy(word)
                    if not preserve_ids:
                        new_word.word_id = None
                    if branch:
                        new_word.set_as_branch(word, self, language_stage)
                    new_word.copied_from = word
                    stage_words.append(new_word)

        # trim sound changes from included words to match language stage
        for word in stage_words:
            word.sound_changes = word.sound_changes_at_stage(language_stage)
            if not include_language_sound_changes:
                word.sound_changes = word.word_sound_changes

        # trim definitions from included words to match language stage
        if not include_all_definitions:
            for word in stage_words:
                definitions = list()
                for definition, stage in word.get_definitions_and_stages():
                    if stage <= language_stage:
                        definitions.append((definition, stage))
                word.clear_definitions()
                if len(definitions) > 0:
                    if branch:
                        word.add_definition(definitions[-1][0], 0)
                    else:
                        for definition, stage in definitions:
                            word.add_definition(definition, stage)

        return stage_words

    def copy_word_at_stage(self, word_id, language_stage=-1, include_previous_stages=True,
                           include_language_sound_changes=True):
        """Return a copy of a word as it existed at a certain language stage.

        The word will include all language sound changes and word sound changes up to and including the specified stage,
        and none from future stages.
        """

        if language_stage < 0:
            language_stage = self.get_current_stage()
        stage_word = None

        # look for the word
        for word in [w for w in self.words if w.word_id == word_id]:  # should only be 1
            if include_previous_stages:
                if word.original_language_stage <= language_stage:
                    word = copy.copy(word)
                    word.word_id = None
                    stage_word = word
            else:
                if word.original_language_stage == language_stage:
                    word = copy.copy(word)
                    word.word_id = None
                    stage_word = word

        # return None if the word was not found at the specified stage
        if stage_word is None:
            return None

        # trim sound changes from the word to match language stage
        stage_word.sound_changes = stage_word.sound_changes_at_stage(language_stage)
        if not include_language_sound_changes:
            stage_word.sound_changes = stage_word.word_sound_changes()

        # trim definitions from the word to match language stage
        definitions = list()
        for definition, stage in stage_word.get_definitions_and_stages():
            if stage <= language_stage:
                definitions.append((definition, stage))
        stage_word.clear_definitions()
        for definition, stage in definitions:
            stage_word.add_definition(definition, stage)

        return stage_word

    def get_sound_changes_at_stage(self, language_stage=-1):
        if language_stage < 0:
            language_stage = self.get_current_stage()
        return [s for s in self.sound_changes if s.stage <= language_stage]

    def get_phonetic_inventory_at_stage(self, language_stage=-1):
        if language_stage < 0:
            language_stage = self.get_current_stage()
        stage_inventory = copy.copy(self.original_phonetic_inventory)
        stage = 0
        while stage <= language_stage:
            stage_words = self.copy_words_at_stage(language_stage=stage, include_previous_stages=False)
            for word in stage_words:
                for syllable in word.get_base_stem():
                    for sound in syllable:
                        if sound not in stage_inventory:
                            stage_inventory.append(sound)
            if stage < language_stage:
                sound_change = self.sound_changes[stage]
                if not sound_change.condition and len(sound_change.old_sounds) == 1:
                    if sound_change.old_sounds[0] in stage_inventory:
                        stage_inventory.remove(sound_change.old_sounds[0])
                if sound_change.new_sounds is not None:
                    for sound in sound_change.new_sounds:
                        if sound not in stage_inventory:
                            stage_inventory.append(sound)
            stage = stage + 1
        return stage_inventory

    def copy_language_at_stage(self, language_stage=-1):
        if language_stage < 0:
            language_stage = self.get_current_stage()
        language = Language(self.name, self.original_phonetic_inventory, self.phonotactics)
        stage = 0
        while stage <= language_stage:
            language.add_words(self.copy_words_at_stage(language_stage=stage, include_previous_stages=False,
                                                        include_language_sound_changes=False,
                                                        include_all_definitions=True))
            if stage < language_stage:
                sound_change = copy.copy(self.sound_changes[stage])
                sound_change.sound_change_rule_id = None
                language.apply_sound_change(sound_change)
            stage = stage + 1
        return language

    def branch_language_at_stage(self, language_stage=-1):
        if language_stage < 0:
            language_stage = self.get_current_stage()
        language = Language('Branch of ' + self.name, self.get_phonetic_inventory_at_stage(language_stage),
                            self.phonotactics)
        language.add_words(self.copy_words_at_stage(language_stage=language_stage, include_previous_stages=True,
                                                    include_language_sound_changes=False, branch=True))
        language.source_language = self
        language.source_language_stage = language_stage
        self.child_languages.append(language)
        return language

    def get_branch_depth(self):
        if self.source_language is None:
            return 0
        else:
            return 1 + self.source_language.get_branch_depth()

    def get_forms_added_at_stage(self, stage):
        return [form for form in self.word_forms if form.original_language_stage == stage]

    def get_forms_at_stage(self, stage):
        return [form for form in self.word_forms if form.original_language_stage <= stage and
                (form.obsoleted_language_stage == -1 or form.obsoleted_language_stage > stage)]

    def add_original_sound(self, sound):
        self.original_phonetic_inventory.append(sound)
        self.modern_phonetic_inventory.append(sound)
