class Sound:
    """One sound represented by, at minimum, an orthographic transcription.

    Each Sound belongs to only one Language.

    Can also (and usually should) contain IPA representation, categories
    for phonotactics (e.g. C for consonant, etc.), relative frequency in
    the language in which it appears, a description, and a number of rules
    for automatic generation of words.
    """

    def __init__(self, orthographic_transcription: str, ipa_transcription: str = '', phonotactics_categories: str = '',
                 frequency: float = 1.0, description: str = ''):
        self.sound_id = None
        self.orthographic_transcription = orthographic_transcription
        self.ipa_transcription = ipa_transcription
        self.phonotactics_categories = phonotactics_categories
        self.frequency = frequency
        self.description = description
        self.can_appear_word_initially = True
        self.can_appear_word_finally = True
        self.can_appear_in_onset = True
        self.can_appear_in_nucleus = True
        self.can_appear_in_coda = True
        self.can_appear_in_clusters = True
        self.can_cluster_self = True
        self.can_duplicate_across_syllable_boundaries = True

    def set_generation_options(self, options: 'int | str'):
        """Set the 8 generation options of this Sound based on one integer.

        :param options: The value of the combined 8 boolean options ranging
        from 0 to 255.
        :type options: int
        """
        try:
            options = int(options)
        except ValueError:
            print('Error parsing sound generation options; allowing everything')
            options = 255
        option_string = bin(options)
        self.can_appear_word_initially = option_string[-1] == '1'
        self.can_appear_word_finally = option_string[-2] == '1'
        self.can_appear_in_onset = option_string[-3] == '1'
        self.can_appear_in_nucleus = option_string[-4] == '1'
        self.can_appear_in_coda = option_string[-5] == '1'
        self.can_appear_in_clusters = option_string[-6] == '1'
        self.can_cluster_self = option_string[-7] == '1'
        self.can_duplicate_across_syllable_boundaries = option_string[-8] == '1'

    def get_generation_options(self) -> int:
        """Return an integer representing the 8 boolean generation options.

        :return: An integer representing the 8 boolean generation options
        ranging in value from 0 (nothing allowed) to 255 (everything allowed).
        :rtype: int
        """
        option_int = 0
        if self.can_appear_word_initially:
            option_int = option_int + 1
        if self.can_appear_word_finally:
            option_int = option_int + 10
        if self.can_appear_in_onset:
            option_int = option_int + 100
        if self.can_appear_in_nucleus:
            option_int = option_int + 1000
        if self.can_appear_in_coda:
            option_int = option_int + 10000
        if self.can_appear_in_clusters:
            option_int = option_int + 100000
        if self.can_cluster_self:
            option_int = option_int + 1000000
        if self.can_duplicate_across_syllable_boundaries:
            option_int = option_int + 10000000
        return int(str(option_int), 2)

    def allowed_by_generation_options(self, syllable_phonotactics: str, syllable_so_far: 'list[Sound]',
                                      previous_syllable: 'list[Sound] | None' = None,
                                      word_initial_syllable: bool = False, word_final_syllable: bool = False) -> bool:
        """Determine if this Sound can appear next by its generation options.

        The previous and current syllables are provided and this Sound is
        tested for addition to the end of the current syllable. If it is to be
        the first Sound in a syllable, the current syllable should be blank.

        Options that cannot be processed based on provided information will
        be skipped over and assumed to pass.

        :param syllable_phonotactics: The phonotactics string used in
        generating the syllable that this Sound is being considered for.
        :type syllable_phonotactics: str
        :param syllable_so_far: The current syllable that this Sound is being
        considered for addition to. Should be an empty list if this Sound is
        to be the first in a new syllable.
        :type syllable_so_far: list[Sound]
        :param previous_syllable: The syllable in the same word as the current
        syllable that precedes the current syllable. Should generally be None
        if the current syllable is the first syllable in a word.
        :type previous_syllable: list[Sound]
        :param word_initial_syllable: Whether the current syllable that this
        Sound is being considered for is the first syllable in a word.
        :type word_initial_syllable: bool
        :param word_final_syllable: Whether the current syllable that this
        Sound is being considered for is the last syllable in a word.
        :type word_final_syllable: bool
        :return: True if this Sound is not forbidden by its (determinable)
        generation options to be appended to the end of syllable_so_far and
        False otherwise.
        :rtype: bool
        """
        if self.get_generation_options() == 255:  # all options are true
            return True

        position = len(syllable_so_far)  # position of next sound to be generated in the syllable_phonotactics string

        if not self.can_appear_word_initially and position == 0 and word_initial_syllable:
            return False
        if not self.can_appear_word_finally and position == len(syllable_phonotactics) - 1 and word_final_syllable:
            return False

        # calculate simplified phonotactics string that only contains V, C, and W
        # using abbreviations from https://chridd.nfshost.com/diachronica/index-diachronica.pdf
        simplified_phonotactics = syllable_phonotactics.upper()
        simplified_phonotactics = simplified_phonotactics.replace('B', 'V').replace('E', 'V').replace('M', 'V')
        simplified_phonotactics = simplified_phonotactics.replace('A', 'C').replace('D', 'C').replace('F', 'C').replace(
            'H', 'C').replace('K', 'C').replace('N', 'C').replace('O', 'C').replace('P', 'C').replace('Q', 'C').replace(
            'R', 'C').replace('S', 'C').replace('T', 'C').replace('Z', 'C').replace('Ḱ', 'C')
        simplified_phonotactics = simplified_phonotactics.replace('J', 'W').replace('L', 'W')

        # calculate onset, nucleus, and coda positions in the phonotactics string
        if 'V' in simplified_phonotactics:
            nucleus_start = simplified_phonotactics.find('V')
            coda_start = simplified_phonotactics.rfind('V') + 1
        else:
            nucleus_start = simplified_phonotactics.find('W')
            coda_start = simplified_phonotactics.rfind('W') + 1

        if nucleus_start != -1:  # if we can't determine a nucleus we can't process these 3
            if not self.can_appear_in_onset and 0 <= position < nucleus_start:
                return False
            if not self.can_appear_in_nucleus and nucleus_start <= position < coda_start:
                return False
            if not self.can_appear_in_coda and coda_start <= position:
                return False

        if not self.can_appear_in_clusters:
            category_at_position = simplified_phonotactics[position]
            if position > 0 and simplified_phonotactics[position-1] == category_at_position:
                return False
            if position < len(simplified_phonotactics) - 1 \
                    and simplified_phonotactics[position+1] == category_at_position:
                return False

        if not self.can_cluster_self and len(syllable_so_far) > 0 and syllable_so_far[-1] == self:
            return False

        if not self.can_duplicate_across_syllable_boundaries and previous_syllable is not None \
                and len(previous_syllable) > 0 and previous_syllable[-1] == self:
            return False

        return True

    def __eq__(self, other):
        if isinstance(other, Sound):
            if self.sound_id and other.sound_id:
                return self.sound_id == other.sound_id
            else:
                return self.orthographic_transcription == other.orthographic_transcription and \
                       self.ipa_transcription == other.ipa_transcription and \
                       self.phonotactics_categories == other.phonotactics_categories and \
                       self.frequency == other.frequency and \
                       self.description == other.description and \
                       self.get_generation_options() == other.get_generation_options()
        else:
            return False

    def __cmp__(self, other):
        if isinstance(other, Sound):
            return self.sound_id == other.sound_id and \
                   self.orthographic_transcription == other.orthographic_transcription and \
                   self.ipa_transcription == other.ipa_transcription and \
                   self.phonotactics_categories == other.phonotactics_categories and \
                   self.frequency == other.frequency and \
                   self.description == other.description and \
                   self.get_generation_options() == other.get_generation_options()
        else:
            return False

    def __hash__(self):
        return hash(self.orthographic_transcription + self.ipa_transcription + self.phonotactics_categories +
                    str(self.frequency) + self.description + str(self.get_generation_options()))

    def __str__(self):
        string = self.orthographic_transcription
        if self.ipa_transcription:
            string = string + ' /' + self.ipa_transcription + '/'
        return string
