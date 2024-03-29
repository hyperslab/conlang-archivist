from conarch import sound_helpers
from conarch.sound import Sound


class SoundChangeRule:
    """A rule for when certain sounds should become different sounds.

    Contains a group of "old" sounds, all of which must be present in
    sequence in a word (or other sequence of sounds) for the change to
    take place and a group of "new" sounds which will replace the "old"
    sounds if the (also contained) condition is met. A condition can be,
    for example, that the old sounds are at the end of a word, that they
    follow a vowel, etc.

    A Sound Change Rule also knows when in the evolution of a language it
    was added in the case that it represents a historical sound change.
    """

    def __init__(self, old_sounds: 'Sound | list[Sound] | None', new_sounds: 'Sound | list[Sound]', condition: str = '',
                 condition_sounds: 'list[Sound] | None' = None, stage: int = -1):
        self.sound_change_rule_id = None
        self.old_sounds = old_sounds
        if type(self.old_sounds) is not list:
            self.old_sounds = [self.old_sounds]
        self.new_sounds = new_sounds
        if self.new_sounds is not None and type(self.new_sounds) is not list:
            self.new_sounds = [self.new_sounds]
        if type(self.new_sounds) is list and len(self.new_sounds) > 0 and self.new_sounds[0] is None:
            self.new_sounds = None
        self.condition = condition
        self.condition_sounds = condition_sounds
        self.stage = stage

    def __str__(self):
        output = ''
        for sound in self.old_sounds:
            if sound is None:
                output = output + 'Ø'
            else:
                output = output + sound.orthographic_transcription
        output = output + ' > '
        if self.new_sounds is None:
            output = output + 'Ø'
        else:
            for sound in self.new_sounds:
                output = output + sound.orthographic_transcription
        if self.condition:
            condition = self.condition
            if '@' in condition and self.condition_sounds is not None:
                for sound in self.condition_sounds:
                    condition.replace('@', sound.orthographic_transcription, 1)
            output = output + ' /' + condition
        return output

    def ipa_str(self) -> str:
        output = ''
        for sound in self.old_sounds:
            if sound is None:
                output = output + 'Ø'
            else:
                output = output + sound.ipa_transcription
        output = output + ' > '
        if self.new_sounds is None:
            output = output + 'Ø'
        else:
            for sound in self.new_sounds:
                output = output + sound.ipa_transcription
        if self.condition:
            condition = self.condition
            if '@' in condition and self.condition_sounds is not None:
                for sound in self.condition_sounds:
                    condition.replace('@', sound.ipa_transcription, 1)
            output = output + ' /' + condition
        return output

    def old_sounds_str(self) -> str:
        return sound_helpers.get_sequence_as_string([self.old_sounds])

    def new_sounds_str(self) -> str:
        return sound_helpers.get_sequence_as_string([self.new_sounds])

    def old_sounds_ipa_str(self) -> str:
        return sound_helpers.get_sequence_as_string([self.old_sounds], use_ipa=True)

    def new_sounds_ipa_str(self) -> str:
        return sound_helpers.get_sequence_as_string([self.new_sounds], use_ipa=True)

    def get_condition_string(self) -> str:
        condition = 'Always'
        if self.condition.count('_') == 1:
            if self.condition == '_#':
                condition = 'Word-Finally'
            elif self.condition == '#_':
                condition = 'Word-Initially'
            elif self.condition == '#_#':
                condition = 'For exact word match'
            elif '_#' in self.condition:
                condition = 'Word-Finally after ' + str(self.condition.split('_#')[0])
            elif '#_' in self.condition:
                condition = 'Word-Initially before ' + str(self.condition.split('#_')[-1])
            elif self.condition[0] == '_':
                condition = 'Preceding ' + str(self.condition.split('_')[-1])
            elif self.condition[-1] == '_':
                condition = 'Following ' + str(self.condition.split('_')[0])
            else:
                condition = 'In between ' + str(self.condition.split('_')[0]) + ' and ' + \
                            str(self.condition.split('_')[-1])
        return condition

    def get_affix_type_string(self) -> str:
        affix_type = 'Infix/Unknown'
        if self.condition.count('_') == 1:
            if self.condition == '#_#':
                affix_type = 'Prefix + Suffix'
            elif '#_' in self.condition:
                affix_type = 'Prefix'
            elif '_#' in self.condition:
                affix_type = 'Suffix'
        return affix_type

    def get_as_conjugation_rule_string(self) -> str:
        return 'Add ' + self.get_affix_type_string() + ' "' + self.new_sounds_str() + \
               '" (/' + self.new_sounds_ipa_str() + '/) ' + self.get_condition_string()

    def map_sounds(self, sound_map: 'dict[Sound, Sound]'):
        if self.old_sounds:
            new_old_sounds = []
            for sound in self.old_sounds:
                if sound in sound_map:
                    new_old_sounds.append(sound_map[sound])
                else:
                    new_old_sounds.append(sound)
            self.old_sounds = new_old_sounds
        if self.new_sounds:
            new_new_sounds = []
            for sound in self.new_sounds:
                if sound in sound_map:
                    new_new_sounds.append(sound_map[sound])
                else:
                    new_new_sounds.append(sound)
            self.new_sounds = new_new_sounds
        if self.condition_sounds:
            new_condition_sounds = []
            for sound in self.condition_sounds:
                if sound in sound_map:
                    new_condition_sounds.append(sound_map[sound])
                else:
                    new_condition_sounds.append(sound)
            self.condition_sounds = new_condition_sounds
