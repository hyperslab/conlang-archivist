import copy
from conarch.sound import Sound
from conarch.sound_change_rule import SoundChangeRule
from conarch.word import Word
import random
from conarch.word_form_rule import WordFormRule


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

    def __init__(self, name: str, phonetic_inventory: 'list[Sound]', phonotactics: str):
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

    def add_word(self, word: Word, language_stage: int = -1):
        """Add a Word to this Language.

        :param word: The Word to add.
        :type word: Word
        :param language_stage: The stage at which the Word will be added. A
        value of -1 (the default) will use the most modern stage.
        :type language_stage: int
        """
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

    def add_words(self, words: 'list[Word]', language_stage: int = -1):
        """Add several words to this Language.

        :param words: The words to add.
        :type words: list[Word]
        :param language_stage: The stage at which the words will be added. A
        value of -1 (the default) will use the most modern stage.
        :type language_stage: int
        """
        for word in words:
            self.add_word(word, language_stage)

    def generate_word(self, min_syllable_length: int = 1, max_syllable_length: int = 2, category: str = '',
                      language_stage: int = -1) -> Word:
        """Create a Word from the phonetic inventory and phonotactics of this
        Language.

        Note that the Word will not be added to the Language as part of this
        method; add_word() must be called separately.

        :param min_syllable_length: The smallest possible number of syllables
        that will be in the Word.
        :type min_syllable_length: int
        :param max_syllable_length: The largest possible number of syllables
        that will be in the Word.
        :type max_syllable_length: int
        :param category: The type of Word to generate, e.g. 'N' for noun.
        :type category: str
        :param language_stage: The stage at which to generate the Word.
        Determines the phonetic inventory used in generation. A value of -1
        (the default) will use the most modern stage.
        :type language_stage: int
        :return: The generated Word.
        :rtype: Word
        """
        return self.generate_words(1, min_syllable_length, max_syllable_length, category=category,
                                   language_stage=language_stage)[0]

    def generate_words(self, words: int = 1, min_syllable_length: int = 1, max_syllable_length: int = 2,
                       category: str = '', language_stage: int = -1) -> 'list[Word]':
        """Create words from the phonetic inventory and phonotactics of this
        Language.

        Note that the words will not be added to the Language as part of this
        method; add_words() must be called separately.

        :param words: The number of words to generate.
        :type words: int
        :param min_syllable_length: The smallest possible number of syllables
        that will be in the words.
        :type min_syllable_length: int
        :param max_syllable_length: The largest possible number of syllables
        that will be in the words.
        :type max_syllable_length: int
        :param category: The type of words to generate, e.g. 'N' for noun.
        :type category: str
        :param language_stage: The stage at which to generate the words.
        Determines the phonetic inventory used in generation. A value of -1
        (the default) will use the most modern stage.
        :type language_stage: int
        :return: The generated words.
        :rtype: list[Word]
        """
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
            new_words.append(Word(stem, category))
        return new_words

    def generate_syllable(self, phonotactics: 'str | None' = None, language_stage: int = -1, word_initial: bool = False,
                          word_final: bool = False, ignore_generation_options: bool = False,
                          previous_syllable: 'list[Sound] | None' = None) -> 'list[Sound]':
        """Create a syllable from the phonetic inventory and phonotactics of
        this Language.

        :param phonotactics: The phonotactics to use for the syllable. A value
        of None (the default) will use the phonotactics from this Language.
        :type phonotactics: str
        :param language_stage: The stage at which to generate the syllable.
        Determines the phonetic inventory used in generation. A value of -1
        (the default) will use the most modern stage.
        :type language_stage: int
        :param word_initial: Whether the syllable is at the start of a Word.
        Affects the sounds that may appear in the syllable.
        :type word_initial: bool
        :param word_final: Whether the syllable is at the end of a Word.
        Affects the sounds that may appear in the syllable.
        :type word_final: bool
        :param ignore_generation_options: If True, generation options in
        potential Sound candidates will be ignored. They will be skipped and
        considered to have all passed. For example, a Sound that normally
        cannot appear at the end of a syllable can now appear there if this
        is True.
        :type ignore_generation_options: bool
        :param previous_syllable: The preceding syllable to the one to be
        generated, if available. Affects the sounds that may appear in the
        syllable.
        :type previous_syllable: list[Sound]
        :return: The generated syllable.
        :rtype: list[Sound]
        """
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

    def apply_sound_change(self, sound_change: SoundChangeRule):
        """Add a historical sound change to this Language.

        The sound change causes a new stage to be created in the Language that
        will be considered the new most modern stage. If sounds are determined
        to be newly added or fully removed because of the sound change, the
        modern phonetic inventory of this Language will change accordingly.

        :param sound_change: A rule defining the sound change. Applies
        indiscriminately to all words in this Language.
        :type sound_change: SoundChangeRule
        """
        sound_change.stage = self.get_current_stage()  # first should be 1
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

    def add_word_form(self, word_form: WordFormRule, use_current_stage: bool = True) -> 'list[Word]':
        """Add a word form (conjugation) to this Language.

        The form will apply to all words in this Language according to the
        original and obsoleted language stage parameters in the rule.

        :param word_form: A rule defining the word form. Contains conjugation
        rules, stage information, and types of words to which the form will
        apply.
        :type word_form: WordFormRule
        :param use_current_stage: If True, the original language stage in
        word_form will be set to the most modern stage of this Language when
        the form is added.
        :type use_current_stage: bool
        :return: The words created as forms of existing words at the time this
        form is added. These should not be added to this Language, as they are
        accessed via the "parent" words they belong to, where they are already
        saved as part of this method.
        :rtype: list[Word]
        """
        if use_current_stage:
            word_form.original_language_stage = self.get_current_stage()
        self.word_forms.append(word_form)
        form_words = []
        for word in self.copy_words_at_stage(word_form.original_language_stage, include_all_definitions=True):
            if any(category in word.categories for category in word_form.categories):
                form_words.append(self.apply_form_to_word(word_form, word.copied_from))
        return form_words

    @staticmethod
    def apply_form_to_word(word_form: WordFormRule, word: Word) -> Word:
        """Add a word form to a Word based on a rule.

        The form will be saved to the Word and returned. This will not check
        if the category of the form matches that of the Word, so check that
        before calling this!

        :param word_form: A rule defining how the word form will be created.
        :type word_form: WordFormRule
        :param word: The Word to add the form to.
        :type word: Word
        :return: The newly created form word.
        :rtype: Word
        """
        return word.add_form_from_rule(word_form)

    def print_all_word_forms(self, include_ipa: bool = False, include_base_stem: bool = False):
        """Write all words and their forms in this Language to standard out.

        :param include_ipa: Whether to include the IPA notation for words.
        :type include_ipa: bool
        :param include_base_stem: Whether to include the original form of each
        Word, unmodified by historical sound changes.
        :type include_base_stem: bool
        """
        for word in self.words:
            divider_length = word.print_all_forms(include_ipa=include_ipa, include_base_stem=include_base_stem)
            print('-' * divider_length)

    def get_full_sound_inventory(self) -> 'list[Sound]':
        """Return all sounds that ever existed in this Language.

        :return: A list of all sounds that ever existed in this Language.
        :rtype: list[Sound]
        """
        sounds = set()
        for i in range(0, self.get_current_stage() + 1):
            for sound in self.get_phonetic_inventory_at_stage(i):
                sounds.add(sound)
        return list(sounds)

    def get_current_stage(self) -> int:
        """Return the most modern stage of this Language.

        A Language will be considered to be at stage 0 when it is created. The
        stage then increments by 1 for every historical sound change applied.

        :return: The most modern stage of this Language.
        :rtype: int
        """
        return len(self.sound_changes)

    def copy_words_at_stage(self, language_stage: int = -1, include_previous_stages: bool = True,
                            include_language_sound_changes: bool = True, branch: bool = False,
                            include_all_definitions: bool = False, preserve_ids: bool = False,
                            include_forms: bool = True) -> 'list[Word]':
        """Return a list containing copies of all words that existed at a
        certain language stage.

        The words will exist as they did at the specified stage, including all
        language sound changes and word sound changes up to and including the
        specified stage, and none from future stages.

        :param language_stage: The stage from which to copy. A value of -1
        (the default) will use the most modern stage.
        :type language_stage: int
        :param include_previous_stages: Whether to include words that were
        added at stages before language_stage as opposed to only those added
        at precisely language_stage.
        :type include_previous_stages: bool
        :param include_language_sound_changes: Whether to include language
        sound changes in the copied words. If False, the words will have an
        empty list in place of language sound changes up to and including the
        specified stage.
        :type include_language_sound_changes: bool
        :param branch: Whether the copied words are to be considered branched
        from their "source" words. This will cause the copies to be linked to
        the "source" words and dependent upon them to calculate their stems.
        :type branch: bool
        :param include_all_definitions: If True, all definitions will be
        copied from the "source" words as opposed to only those from stages up
        to and including language_stage.
        :type include_all_definitions: bool
        :param preserve_ids: If False, copied words will all have their ID set
        to None. Otherwise, it will be equal to the "source" word's ID which
        may cause data issues when saving.
        :type preserve_ids: bool
        :param include_forms: Whether to include form words in copies. If
        False, copied words will have no forms. If True, they will have all
        forms that their "source" words had, even those that did not exist at
        language_stage (though such forms should generally never appear if
        properly accessed). TODO filter newer forms out?
        :type include_forms: bool
        :return: The copied words.
        :rtype: list[Word]
        """

        if language_stage < 0:
            language_stage = self.get_current_stage()
        stage_words = list()

        # determine which words to include
        for word in self.words:
            if include_previous_stages:
                if word.original_language_stage <= language_stage:
                    new_word = copy.deepcopy(word)
                    if not preserve_ids:
                        new_word.word_id = None
                    if not include_forms:
                        new_word.word_forms = []
                    if not preserve_ids and include_forms:
                        for form in new_word.word_forms:
                            form.word_id = None
                    if branch:
                        new_word.set_as_branch(word, language_stage)
                    new_word.copied_from = word
                    stage_words.append(new_word)
            else:
                if word.original_language_stage == language_stage:
                    new_word = copy.deepcopy(word)
                    if not preserve_ids:
                        new_word.word_id = None
                    if not include_forms:
                        new_word.word_forms = []
                    if not preserve_ids and include_forms:
                        for form in new_word.word_forms:
                            form.word_id = None
                    if branch:
                        new_word.set_as_branch(word, language_stage)
                    new_word.copied_from = word
                    stage_words.append(new_word)

        # trim sound changes from included words to match language stage
        for word in stage_words:
            word.word_sound_changes = [s for s in word.word_sound_changes if s.stage <= language_stage]
            if include_language_sound_changes:
                word.language_sound_changes = [s for s in word.language_sound_changes if s.stage <= language_stage]
            else:
                word.language_sound_changes = []

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

    def get_sound_changes_at_stage(self, language_stage: int = -1) -> 'list[SoundChangeRule]':
        """Return all historical sound changes present at a given stage.

        The number of stages returned should be the same as the stage of
        reference, e.g. a language_stage of 2 should return 2 sound changes.

        :param language_stage: The langauge stage of the most recent sound
        change desired. A value of -1 (the default) will use the most modern
        stage and cause all historical sound changes to be returned.
        :type language_stage: int
        :return: All historical sound changes from stages up to and including
        language_stage in order from earliest to most modern.
        :rtype: list[SoundChangeRule]
        """
        if language_stage < 0:
            language_stage = self.get_current_stage()
        return [s for s in self.sound_changes if s.stage <= language_stage]

    def get_phonetic_inventory_at_stage(self, language_stage: int = -1) -> 'list[Sound]':
        """Return the phonetic inventory of this Language at a given stage.

        Starts with the original phonetic inventory as a basis, then goes
        through each language stage up to language_stage adding and removing
        sounds based on sound changes and added words.

        :param language_stage: The language stage to pull the phonetic
        inventory from. A value of -1 (the default) will use the most modern
        stage and cause the modern phonetic inventory to be returned.
        :type language_stage: int
        :return: All sounds present in this Language at language_stage.
        :rtype: list[Sound]
        """
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

    def copy_language_at_stage(self, language_stage: int = -1) -> 'Language':
        """Return a copy of this Language as it existed at a given stage.

        Uses the "newest" form of the Language from the stage. In other words,
        includes all words and word forms that were added during the given
        stage.

        :param language_stage: The stage of this Language to copy. A value of
        -1 (the default) will use the most modern stage.
        :type language_stage: int
        :return: A copy of this Language as it existed at a given stage.
        :rtype: Language
        """
        if language_stage < 0:
            language_stage = self.get_current_stage()
        language = Language(self.name, self.original_phonetic_inventory, self.phonotactics)
        language.add_words(self.copy_words_at_stage(language_stage=language_stage, include_previous_stages=True,
                                                    include_language_sound_changes=False,
                                                    include_all_definitions=True, include_forms=False))
        for form in copy.deepcopy(self.get_forms_at_stage(language_stage)):
            language.add_word_form(form, use_current_stage=False)
        for stage_change in self.sound_changes[:language_stage]:
            sound_change = copy.copy(stage_change)
            sound_change.sound_change_rule_id = None
            language.apply_sound_change(sound_change)
        sound_map = dict(zip(language.get_full_sound_inventory(), copy.deepcopy(language.get_full_sound_inventory())))
        language.map_sounds(sound_map)
        return language

    def branch_language_at_stage(self, language_stage: int = -1) -> 'Language':
        """Return a branch of this Language as it existed at a given stage.

        Branched languages essentially take a "snapshot" of their "source"
        Language and convert that to a new, stage 0 Language. All words in the
        source Language from the given stage will be in the branched Language,
        but all sound changes up to the stage will be abstracted away so that
        the stage 0 form of the Word in the branched Language will be equal to
        the stage X form of the Word from the source language, X being
        language_stage. Word forms behave similarly. The original phonetic
        inventory of the branched Language will be equivalent to the phonetic
        inventory of the source Language from language_stage. No historical
        sound changes will be present in the branched Language upon creation,
        since all sound changes have been "condensed" into stage 0.

        Changing the source Language at or before language_stage will cause
        changes to propagate to the branched Language as if the branch was
        recreated following the change. Changing the source Language after
        language_stage will not affect the branch, and no change to a branch
        can affect its source Language.

        Uses the "newest" form of the Language from the stage. In other words,
        includes all words and word forms that were added during the given
        stage.

        :param language_stage: The stage of this Language to copy. A value of
        -1 (the default) will use the most modern stage.
        :type language_stage: int
        :return: A copy of this Language as it existed at a given stage.
        :rtype: Language
        """
        if language_stage < 0:
            language_stage = self.get_current_stage()
        language = Language('Branch of ' + self.name, self.get_phonetic_inventory_at_stage(language_stage),
                            self.phonotactics)
        language.add_words(self.copy_words_at_stage(language_stage=language_stage, include_previous_stages=True,
                                                    include_language_sound_changes=False, branch=True,
                                                    include_forms=False))
        for form in copy.deepcopy(self.get_forms_at_stage(language_stage)):
            language.add_word_form(form, use_current_stage=False)
            form.original_language_stage = 0
            form.obsoleted_language_stage = -1
        language.source_language = self
        language.source_language_stage = language_stage
        self.child_languages.append(language)
        return language

    def get_branch_depth(self) -> int:
        """Return the "depth" of this Language in terms of branching.

        A Langauge that is not branched will return 0. A Language that is
        branched from a non-branched Language will return 1. A Language that
        is branched from a branched Langauge that itself is not a branched
        Language will return 2, and so on.

        :return: The "depth" of this Language in terms of branching.
        :rtype: int
        """
        if self.source_language is None:
            return 0
        else:
            return 1 + self.source_language.get_branch_depth()

    def get_forms_added_at_stage(self, stage: int) -> 'list[WordFormRule]':
        """Return all word forms added precisely at a given language stage.

        Omits all forms added before or after the given stage.

        Note that this method returns rules representing the forms, not the
        form words themselves.

        :param stage: The language stage to consider.
        :type stage: int
        :return: Rules representing all word forms in the Language from the
        given stage.
        :rtype: list[WordFormRule]
        """
        return [form for form in self.word_forms if form.original_language_stage == stage]

    def get_forms_at_stage(self, stage: int) -> 'list[WordFormRule]':
        """Return all word forms added at or before a given language stage.

        Note that this method returns rules representing the forms, not the
        form words themselves.

        :param stage: The language stage to consider.
        :type stage: int
        :return: Rules representing all word forms in the Language from the
        given stage.
        :rtype: list[WordFormRule]
        """
        return [form for form in self.word_forms if form.original_language_stage <= stage and
                (form.obsoleted_language_stage == -1 or form.obsoleted_language_stage > stage)]

    def add_original_sound(self, sound: Sound):
        """Add a Sound to the original phonetic inventory of this Language.

        :param sound: The Sound to add.
        :type sound: Sound
        """
        self.original_phonetic_inventory.append(sound)
        self.modern_phonetic_inventory.append(sound)  # TODO recalculate this somehow instead of just adding

    def map_sounds(self, sound_map: 'dict[Sound, Sound]'):
        """Convert specified sounds in this Language into new sounds.

        Includes sounds in all the words, word forms, sound changes, etc. in
        this Language.

        Every instance of each Sound provided will be converted into the same
        Sound, so the number of sounds in this Language will not change unless
        the same Sound is provided as the target of multiple mappings.

        :param sound_map: A dictionary representing sounds to map. The keys
        are the sounds to change and the values are the sounds to change them
        into.
        :type sound_map: dict[Sound, Sound]
        """
        new_original_phonetic_inventory = []
        for sound in self.original_phonetic_inventory:
            if sound in sound_map:
                new_original_phonetic_inventory.append(sound_map[sound])
            else:
                new_original_phonetic_inventory.append(sound)
        self.original_phonetic_inventory = new_original_phonetic_inventory
        new_modern_phonetic_inventory = []
        for sound in self.modern_phonetic_inventory:
            if sound in sound_map:
                new_modern_phonetic_inventory.append(sound_map[sound])
            else:
                new_modern_phonetic_inventory.append(sound)
        self.modern_phonetic_inventory = new_modern_phonetic_inventory
        for word in self.words:
            word.map_sounds(sound_map)
        for sound_change in self.sound_changes:
            sound_change.map_sounds(sound_map)
        for form_rule in self.word_forms:
            form_rule.map_sounds(sound_map)
