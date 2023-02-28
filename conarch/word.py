import copy
from conarch import sound_helpers
import itertools
from conarch import id_assigner


class Word:
    """One word represented by a number of sounds and sound changes.

    Each Word belongs to only one Language and knows both when in the
    language's evolution it was added to the Language and when it was
    removed ("obsoleted").

    The Word knows all historical sound changes from the Language it
    belongs to so that it can modify itself to fit any stage as well as
    any sound changes that apply, for whatever reason, to this Word alone.

    A Word is either a "stem" representing a single morpheme or a "form"
    that represents a conjugation of the "stem" (e.g. plural for nouns,
    perfective for verbs, etc.). A stem knows all of its forms, and a form
    knows its stem. Forms do not have their own sounds, but are calculated
    based on their stem and a number of sound change rules.

    A Word can also be "derived" from another Word that may be in the same
    Language or a different one. Derived words, like forms, are calculated
    based on their "source" Word and a number of sound change rules.

    In addition, a Word can have up to one definition for each stage it
    has existed in its Language. Its "current" definition at any stage in
    which it was not defined is simply pulled from the most recent stage
    (at the time) in which it was.
    """

    def __init__(self, base_stem, categories='', original_language_stage=0, assign_id=True):
        self.word_id = None
        if assign_id:
            self.word_id = id_assigner.new_word_id()
        self.base_stem = base_stem  # don't access this directly unless you're sure the word is not branched etc.
        self.categories = categories
        self.language_sound_changes = list()  # inherited from the language; should be same as language.sound_changes
        self.word_sound_changes = list()  # unique to this word
        self.original_language_stage = original_language_stage  # the stage the word was added to its language
        self.obsoleted_language_stage = -1  # the stage the word was removed from its language
        self.definitions = dict()  # [stage] = definition
        self.source_word = None  # only populated if this word is derived from another word
        self.source_word_language_stage = None  # only populated if this word is derived from another word
        self.word_forms = list()  # list of child words that represent conjugations etc. of this word
        self.stem_word = None  # only populated if this is a form of another word
        self.stem_word_language_stage = None  # only populated if this is a form of another word
        self.word_form_name = None  # only populated if this is a form of another word
        self.copied_from = None  # not saved to db, only for language.copy_words functions

    def get_base_stem(self):
        if self.is_word_form():
            return self.stem_word.get_stem_at_stage(self.stem_word_language_stage)
        elif not self.has_source_word():
            return self.base_stem
        else:
            return self.source_word.get_stem_at_stage(self.source_word_language_stage)

    def set_as_branch(self, source_word, source_word_language_stage):
        self.source_word = source_word
        self.source_word_language_stage = source_word_language_stage
        self.base_stem = None

    def add_form_word(self, form_word, stage=-1):
        """Add a Word to this Word as a conjugated form.

        The form will automatically inherit all language sound changes and
        word sound changes from this Word as well as automatically generate
        definitions based on those in this Word.

        Note that there is no need to add a base stem to the form, as words
        that are forms of other words will use their "parent" word's stem from
        the stage at which the form was added as their base stem. From there,
        language sound changes will apply to parent words and their forms
        separately, causing natural irregularities in conjugations.
        """

        form_word.stem_word = self
        form_word.stem_word_language_stage = max(stage, self.original_language_stage)
        form_word.language_sound_changes = copy.copy(self.language_sound_changes)
        form_word.word_sound_changes = copy.copy(self.word_sound_changes)
        if form_word.word_form_name is None:
            form_word.word_form_name = 'Unnamed'
        for d_stage, definition in self.definitions.items():
            form_word.add_definition(form_word.word_form_name + ' form of a word meaning: ' + definition, d_stage)
        self.word_forms.append(form_word)
        return form_word

    def add_form_from_rule(self, word_form):
        """Create a Word from a word form rule as a form for this Word.

        The form will determine its name, original stage, obsoleted stage, and
        conjugation rules (in the form of word sound changes) from the word
        form rule. It will inherit everything else it needs from this Word as
        described in add_form_word.
        """

        form_word = Word(None, self.categories, max(word_form.original_language_stage, self.original_language_stage))
        form_word.word_form_name = word_form.name
        if self.obsoleted_language_stage > -1 < word_form.obsoleted_language_stage:
            form_word.obsoleted_language_stage = min(self.obsoleted_language_stage,
                                                     word_form.obsoleted_language_stage)
        else:  # little trick to use whichever is not -1, or -1 if they both are, since it will never be < -1
            form_word.obsoleted_language_stage = max(self.obsoleted_language_stage,
                                                     word_form.obsoleted_language_stage)
        for conjugation_rule in word_form.get_adjusted_rules():  # forms have a None base stem and are calculated on the
            form_word.add_word_sound_change(conjugation_rule)  # fly; the rules are located in the word sound changes
            conjugation_rule.stage = form_word.original_language_stage
        return self.add_form_word(form_word, word_form.original_language_stage)

    def has_source_word(self):
        return True if self.source_word else False  # not a boolean so this is fine

    def is_word_form(self):
        return True if self.stem_word else False  # not a boolean so this is fine

    def __str__(self):
        return self.get_modern_stem_string(include_ipa=False)

    def add_definition(self, definition, language_stage):
        self.definitions[language_stage] = definition

    def get_definitions_and_stages(self):
        for stage, definition in self.definitions.items():
            yield definition, stage

    def get_definition_at_stage(self, language_stage, exact=False):
        if language_stage in self.definitions.keys():
            return self.definitions[language_stage]
        elif not exact:  # find most recent definition
            defined_stages = list(self.definitions.keys())
            defined_stages.sort()
            while language_stage not in defined_stages:
                language_stage = language_stage - 1
                if language_stage < 0:  # the word was not defined by the provided stage
                    return ''
            return self.definitions[language_stage]
        else:
            return ''

    def get_definition_stage_at_stage(self, language_stage):
        if language_stage in self.definitions.keys():
            return self.definitions[language_stage]
        else:  # find most recent definition
            defined_stages = list(self.definitions.keys())
            defined_stages.sort()
            while language_stage not in defined_stages:
                language_stage = language_stage - 1
                if language_stage < 0:  # the word was not defined by the provided stage
                    return -1
            return language_stage

    def clear_definitions(self):
        self.definitions = dict()

    def has_definition_at_stage(self, language_stage, exact=False):
        if language_stage in self.definitions.keys():
            return True
        elif not exact:  # find most recent definition
            defined_stages = list(self.definitions.keys())
            defined_stages.sort()
            while language_stage not in defined_stages:
                language_stage = language_stage - 1
                if language_stage < 0:  # the word was not defined by the provided stage
                    return False
            return True
        else:
            return False

    def add_language_sound_change(self, sound_change):
        self.language_sound_changes.append(sound_change)
        for form in self.word_forms:
            form.add_language_sound_change(sound_change)

    def add_word_sound_change(self, sound_change):
        if sound_change.stage == -1:  # word sound changes need a stage to function correctly
            sound_change.stage = self.get_current_stage()  # it is still recommended to set this manually before calling
        self.word_sound_changes.append(sound_change)

    def all_sound_changes(self):
        """Gets all sound changes, in order, that apply to the modern word."""
        ordered_sound_changes = list()
        # add all language sound changes and word sound changes that correspond to a language stage
        for i in range(self.original_language_stage, self.get_current_stage()):
            for word_sound_change in [s for s in self.word_sound_changes if s.stage == i]:
                ordered_sound_changes.append(word_sound_change)
            ordered_sound_changes.append(self.language_sound_changes[i])
        # add word sound changes from stages at or beyond the highest language stage
        for word_sound_change in sorted([s for s in self.word_sound_changes if s.stage >= self.get_current_stage()],
                                        key=lambda s: s.stage):
            ordered_sound_changes.append(word_sound_change)
        return ordered_sound_changes

    def sound_changes_at_stage(self, stage):
        return [s for s in self.all_sound_changes() if s.stage <= stage]

    @staticmethod
    def get_stem_string(stem, include_ipa=False):
        orthography = ''
        ipa = ''
        for syllable in stem:
            for s in syllable:
                orthography = orthography + s.orthographic_transcription
                if include_ipa:
                    ipa = ipa + s.ipa_transcription
        if include_ipa and ipa:
            return orthography + ' /' + ipa + '/'
        else:
            return orthography

    def get_base_stem_string(self, include_ipa=False):
        return self.get_stem_string(self.get_base_stem(), include_ipa=include_ipa)

    def print_base_stem(self, include_ipa=False):
        print(self.get_base_stem_string(include_ipa=include_ipa))

    def get_modern_stem(self):
        modern_stem = copy.deepcopy(self.get_base_stem())
        for sound_change in self.all_sound_changes():
            modern_stem = sound_helpers.change_sounds(modern_stem, sound_change.old_sounds, sound_change.new_sounds,
                                                      sound_change.condition, sound_change.condition_sounds)
        return modern_stem

    def get_modern_stem_string(self, include_ipa=False):
        return self.get_stem_string(self.get_modern_stem(), include_ipa=include_ipa)

    def print_modern_stem(self, include_ipa=False):
        print(self.get_modern_stem_string(include_ipa=include_ipa))

    def get_stem_at_stage(self, stage):
        stage_stem = copy.deepcopy(self.get_base_stem())
        for sound_change in self.sound_changes_at_stage(stage):
            stage_stem = sound_helpers.change_sounds(stage_stem, sound_change.old_sounds, sound_change.new_sounds,
                                                     sound_change.condition, sound_change.condition_sounds)
        return stage_stem

    def get_stem_string_at_stage(self, stage, include_ipa=False):
        return self.get_stem_string(self.get_stem_at_stage(stage), include_ipa=include_ipa)

    def print_stem_at_stage(self, stage, include_ipa=False):
        print(self.get_stem_string_at_stage(stage, include_ipa=include_ipa))

    def get_form(self, form_name):
        if form_name == 'Stem':
            return self.get_modern_stem()
        for form in self.word_forms:
            if form.word_form_name == form_name:
                return form.get_modern_stem()

    def print_form(self, form_name, include_ipa=False):
        orthography = ''
        ipa = ''
        form = self.get_form(form_name)
        for syllable in form:
            for s in syllable:
                orthography = orthography + s.orthographic_transcription
                if include_ipa:
                    ipa = ipa + s.ipa_transcription
        if include_ipa and ipa:
            print(orthography + ' /' + ipa + '/')
        else:
            print(orthography)

    def get_all_forms_and_names(self, include_base_stem=False, include_modern_stem=True):
        final_forms = list()
        used_forms = list()
        if include_base_stem:
            final_forms.append(copy.deepcopy(self.get_base_stem()))
            used_forms.append('Old Stem')
        form_names = list()
        if include_modern_stem:
            form_names.append('Stem')
        for word_form in self.word_forms:
            form_names.append(word_form.word_form_name)
        for form_name in form_names:
            final_forms.append(self.get_form(form_name))
            used_forms.append(form_name)
        return final_forms, used_forms

    def get_all_form_and_name_strings(self, include_ipa=False, include_base_stem=False, include_modern_stem=True):
        form_list, form_name_list = self.get_all_forms_and_names(include_base_stem=include_base_stem,
                                                                 include_modern_stem=include_modern_stem)
        form_names = list()
        orthographies = list()
        ipas = list()
        longest_form_name = 0
        longest_orthography = 0
        for form, form_name in zip(form_list, form_name_list):
            orthography = ''
            ipa = ''
            for syllable in form:
                for s in syllable:
                    orthography = orthography + s.orthographic_transcription
                    if include_ipa:
                        ipa = ipa + s.ipa_transcription
            if form_name:
                form_names.append(form_name)
                if len(form_name) > longest_form_name:
                    longest_form_name = len(form_name)
            if include_ipa and ipa:
                ipas.append(ipa)
            orthographies.append(orthography)
            if len(orthography) > longest_orthography:
                longest_orthography = len(orthography)
        for form_name, orthography, ipa in itertools.zip_longest(form_names, orthographies, ipas):
            print_string = orthography.ljust(longest_orthography)
            if form_name:
                print_string = form_name.ljust(longest_form_name) + ' | ' + print_string
            if ipa:
                print_string = print_string + ' /' + ipa + '/'
            yield print_string

    def print_all_forms(self, include_ipa=False, include_base_stem=False):
        form_list, form_name_list = self.get_all_forms_and_names(include_base_stem=include_base_stem)
        form_names = list()
        orthographies = list()
        ipas = list()
        longest_form_name = 0
        longest_orthography = 0
        for form, form_name in zip(form_list, form_name_list):
            orthography = ''
            ipa = ''
            for syllable in form:
                for s in syllable:
                    orthography = orthography + s.orthographic_transcription
                    if include_ipa:
                        ipa = ipa + s.ipa_transcription
            if form_name:
                form_names.append(form_name)
                if len(form_name) > longest_form_name:
                    longest_form_name = len(form_name)
            if include_ipa and ipa:
                ipas.append(ipa)
            orthographies.append(orthography)
            if len(orthography) > longest_orthography:
                longest_orthography = len(orthography)
        longest_print_string = 0
        for form_name, orthography, ipa in itertools.zip_longest(form_names, orthographies, ipas):
            print_string = orthography.ljust(longest_orthography)
            if form_name:
                print_string = form_name.ljust(longest_form_name) + ' | ' + print_string
            if ipa:
                print_string = print_string + ' /' + ipa + '/'
            print(print_string)
            if len(print_string) > longest_print_string:
                longest_print_string = len(print_string)
        return longest_print_string

    def is_empty(self):
        if self.get_base_stem() is not None:
            for syllable in self.get_base_stem():
                if syllable is not None:
                    for sound in syllable:
                        if sound is not None:
                            return False
        return True

    def get_current_stage(self):
        if self.obsoleted_language_stage >= 0:
            return min(len(self.language_sound_changes), self.obsoleted_language_stage)
        else:
            return len(self.language_sound_changes)

    def fits_phonotactics(self, phonotactics, test_base_stem=False):
        """Check if the Word is compatible with the given phonotactics string.

        Compares each syllable in the Word to the phonotactics and returns
        False if any syllable is incompatible.

        Supports (), {}, and numbers in the phonotactics string.
        """
        test_stem = self.get_modern_stem() if not test_base_stem else self.get_base_stem()
        phonotactics.translate(dict.fromkeys(map(ord, u"1234567890,")))  # don't care about these characters

        def split_parenthesis(tactics):
            """Create a list of all possible resolutions of parentheses in a phonotactics string."""
            for i, char in enumerate(tactics):
                if char == '(':
                    j = i
                    layer = 1
                    while layer > 0:
                        j = j + 1
                        if tactics[j] == '(':
                            layer = layer + 1
                        elif tactics[j] == ')':
                            layer = layer - 1
                    excluded = split_parenthesis(tactics[:i] + tactics[j+1:])  # without content in parentheses
                    included = split_parenthesis(tactics[:i] + tactics[i+1:j] + tactics[j+1:])  # including it
                    return excluded + included
            return [tactics]  # string contains no parentheses (base case)

        possibilities = []
        for possibility in split_parenthesis(phonotactics):  # resolve {} brackets
            parsed = []
            index = 0
            while index < len(possibility):
                if possibility[index] != '{':
                    parsed.append(possibility[index])
                else:
                    sounds = ''
                    index = index + 1
                    while possibility[index] != '}':
                        sounds = sounds + possibility[index]
                        index = index + 1
                    parsed.append(sounds)
                index = index + 1
            possibilities.append(parsed)

        # see if each syllable matches at least one possible resolution of the phonotactics
        for syllable in test_stem:  # kind of a brute-force approach but this won't be called much so probably ok
            syllable_tactics = [s.phonotactics_categories for s in syllable]
            found_possibility = False
            for possibility in possibilities:
                if len(possibility) != len(syllable_tactics):
                    continue
                for p, st in zip(possibility, syllable_tactics):
                    if len(st) == 1 and st not in p:
                        continue
                    found = False
                    for category in st:
                        if category in p:
                            found = True
                    if not found:
                        continue
                found_possibility = True
                break
            if not found_possibility:
                return False

        return True

    def get_base_sounds(self):
        for syllable in self.get_base_stem():
            for sound in syllable:
                yield sound

    def get_modern_sounds(self):
        for syllable in self.get_modern_stem():
            for sound in syllable:
                yield sound
