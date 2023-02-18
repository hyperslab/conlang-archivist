import copy
from src import sound_helpers
import itertools
from src import id_assigner


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
        self.language_sound_changes = list()  # inherited from the language and applies to all words in it
        self.word_sound_changes = list()  # unique to this word
        self.original_language_stage = original_language_stage  # the stage the word was added to its language
        self.obsoleted_language_stage = -1  # the stage the word was removed from its language
        self.definitions = dict()  # [stage] = definition
        self.source_word_id = None  # only populated if this word is derived from another word
        self.source_word_language = None  # only populated if this word is derived from another word
        self.source_word_language_stage = None  # only populated if this word is derived from another word
        self.word_forms = list()  # list of child words that represent conjugations etc. of this word
        self.stem_word_id = None  # only populated if this is a form of another word
        self.stem_word_language = None  # only populated if this is a form of another word
        self.stem_word_language_stage = None  # only populated if this is a form of another word
        self.word_form_name = None  # only populated if this is a form of another word
        self.copied_from = None  # not saved to db, only for language.copy_words functions

    def get_base_stem(self):
        if self.is_word_form():
            return self.stem_word_language.copy_word_at_stage(self.stem_word_id,
                                                              self.stem_word_language_stage).get_modern_stem()
        elif not self.has_source_word():
            return self.base_stem
        else:
            return self.source_word_language.copy_word_at_stage(self.source_word_id,
                                                                self.source_word_language_stage).get_modern_stem()

    def set_as_branch(self, source_word, source_word_language, source_word_language_stage):
        self.source_word_id = source_word.word_id
        self.source_word_language = source_word_language
        self.source_word_language_stage = source_word_language_stage
        self.base_stem = None

    def has_source_word(self):
        return True if self.source_word_id else False

    def is_word_form(self):
        return True if self.word_form_name else False

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
        self.word_sound_changes.append(sound_change)

    def all_sound_changes(self):
        ordered_sound_changes = list()
        i = 0
        for language_sound_change in self.language_sound_changes:
            ordered_sound_changes.append(language_sound_change)
            for word_sound_change in [s for s in self.word_sound_changes if s.stage == i]:
                ordered_sound_changes.append(word_sound_change)
            i = i + 1
        for word_sound_change in sorted([s for s in self.word_sound_changes if s.stage >= i],
                                        key=lambda s: s.word_change_stage):
            ordered_sound_changes.append(word_sound_change)
        return ordered_sound_changes

    def sound_changes_at_stage(self, stage):
        return [s for s in self.all_sound_changes() if s.stage <= stage]

    def get_base_stem_string(self, include_ipa=False):
        orthography = ''
        ipa = ''
        for syllable in self.get_base_stem():
            for s in syllable:
                orthography = orthography + s.orthographic_transcription
                if include_ipa:
                    ipa = ipa + s.ipa_transcription
        if include_ipa and ipa:
            return orthography + ' /' + ipa + '/'
        else:
            return orthography

    def print_base_stem(self, include_ipa=False):
        print(self.get_base_stem_string(include_ipa=include_ipa))

    def get_modern_stem(self):
        modern_stem = copy.deepcopy(self.get_base_stem())
        for sound_change in self.all_sound_changes():
            modern_stem = sound_helpers.change_sounds(modern_stem, sound_change.old_sounds, sound_change.new_sounds,
                                                      sound_change.condition, sound_change.condition_sounds)
        return modern_stem

    def get_modern_stem_string(self, include_ipa=False):
        orthography = ''
        ipa = ''
        modern_stem = self.get_modern_stem()
        for syllable in modern_stem:
            for s in syllable:
                orthography = orthography + s.orthographic_transcription
                if include_ipa:
                    ipa = ipa + s.ipa_transcription
        if include_ipa and ipa:
            return orthography + ' /' + ipa + '/'
        else:
            return orthography

    def print_modern_stem(self, include_ipa=False):
        print(self.get_modern_stem_string(include_ipa=include_ipa))

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
