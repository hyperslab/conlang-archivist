import copy

from conarch.sound_change_rule import SoundChangeRule
from conarch import sound_helpers


class WordFormRule:
    """Contains conjugation rules for creating a word form.

    Knows the name of the form, the categories of Word that the form can
    be created from (e.g. N for noun, etc.), and the point in the
    evolution of its Language in which the form was first created.

    The rules themselves are represented each by a Sound Change Rule. All
    rules will be executed on each word when generating the form, so it is
    important to ensure the conditions for the rules are mutually
    exclusive if there are multiple ways to derive the form (unless you
    deliberately want multiple conjugation steps, which is also possible).

    A Word Form Rule will also keep track of historical sound changes that
    apply to the language it belongs to and can "adjust" each Sound Change
    Rule to conform to a given stage of a language. (note: incomplete)
    """

    def __init__(self, name, categories='', original_language_stage=0):
        self.word_form_rule_id = None
        self.name = name  # the name of the form, e.g. 'Plural' 'Genitive' etc.
        self.categories = categories  # the types of word to which the rule applies, represented as 'N' 'VA' etc.
        self.base_form_rules = []  # the sound change rules that are applied to create the form as of the original stage
        self.sound_changes = []  # the sound change rules that have affected the form over time
        self.original_language_stage = original_language_stage  # the stage the form was added to the language
        self.obsoleted_language_stage = -1  # the stage the form was removed from the language

    def add_suffix_rule(self, suffix, word_end_sound_type=''):
        if type(suffix) is not list:
            suffix = [suffix]
        suffix_rule = SoundChangeRule(None, suffix, condition=word_end_sound_type + '_#',
                                      stage=self.original_language_stage)
        self.base_form_rules.append(suffix_rule)

    def add_prefix_rule(self, prefix, word_start_sound_type=''):
        if type(prefix) is not list:
            prefix = [prefix]
        prefix_rule = SoundChangeRule(None, prefix, condition='#_' + word_start_sound_type,
                                      stage=self.original_language_stage)
        self.base_form_rules.append(prefix_rule)

    def add_custom_rule(self, rule):
        rule.stage = self.original_language_stage
        self.base_form_rules.append(rule)

    def clear_rules(self):
        self.base_form_rules = []

    def get_adjusted_rules(self, stage=-1):  # TODO apply sound changes to rules
        for sound_change in self.base_form_rules:
            sound_change.sound_change_rule_id = None  # reset id here or the db save/load won't preserve them separately
            yield copy.copy(sound_change)

    def get_adjusted_rule_strings(self, stage=-1):
        for sound_change in self.get_adjusted_rules(stage=stage):
            yield sound_change.get_as_conjugation_rule_string()

    def transform_sequence(self, sequence):
        for sound_change in self.get_adjusted_rules():
            sequence = sound_helpers.change_sounds(sequence, sound_change.old_sounds, sound_change.new_sounds,
                                                   sound_change.condition, sound_change.condition_sounds)
        return sequence

    def map_sounds(self, sound_map):
        for rule in self.base_form_rules:
            rule.map_sounds(sound_map)
        for sound_change in self.sound_changes:
            sound_change.map_sounds(sound_map)
