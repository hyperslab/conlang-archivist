import copy
from conarch.sound import Sound


def get_nearby_sound(sequence: 'list[list[Sound]]', i: int, j: int, steps: int = 1, backwards: bool = False) -> Sound:
    """Return a Sound in a sequence a certain number of sounds away.

    Works across syllables, so the next Sound after the last Sound in a
    syllable will be the first Sound in the next syllable.

    1 step will return the Sound following the current Sound, 2 will
    return the Sound after that, and so on. -1 steps will return the Sound
    preceding the current Sound.

    If there is no Sound at the target position, return a new Sound
    represented by the character '#'.

    :param sequence: The sequence of sounds.
    :type sequence: list[list[Sound]]
    :param i: The index of the syllable of the current Sound. 0 refers to
    the first syllable in a sequence.
    :type i: int
    :param j: The index of the current Sound within its syllable. 0 refers
    to the first Sound in a syllable.
    :type j: int
    :param steps: The distance between the current Sound and the target
    Sound.
    :type steps: int
    :param backwards: Whether to search in the opposite direction implied
    by the sign of the 'steps' parameter.
    :type backwards: bool
    :return: The Sound at the target position, or a new Sound represented
    by '#' if there is no Sound there.
    :rtype: Sound
    """
    # to refer from a hypothetical character after the end of a sequence, leave i and increment j by 1
    # i.e. don't start a new syllable
    assert steps != 0
    if i < 0:
        return Sound('#', phonotactics_categories='#')
    if steps < 0:
        backwards = not backwards
        steps = steps * -1
    ii = i
    jj = j
    stepped = 0
    if not backwards:
        while stepped < steps:
            if jj < len(sequence[ii]):
                jj = jj + 1
            if jj >= len(sequence[ii]):
                ii = ii + 1
                jj = 0
            stepped = stepped + 1
        if ii < len(sequence) and jj < len(sequence[ii]):
            return sequence[ii][jj]
        else:
            return Sound('#', phonotactics_categories='#')
    else:
        while stepped < steps:
            if jj > 0:
                jj = jj - 1
                stepped = stepped + 1
            elif ii > 0:
                ii = ii - 1
                jj = len(sequence[ii]) - 1
                stepped = stepped + 1
            else:
                return Sound('#', phonotactics_categories='#')
        return sequence[ii][jj]


def check_condition(sequence: 'list[list[Sound]]', i1: int, j1: int, i2: int, j2: int, condition: str,
                    condition_sounds: 'list[Sound] | None' = None) -> bool:
    """Check if a Sound (or sounds) in a sequence matches a condition.

    For example, the condition '_#' looks for sounds at the end of a word.
    This function will return True for this condition if a provided Sound
    is at the end of its sequence, or in the case of multiple sounds, if
    the entire subsequence is at the end of its sequence.

    :param sequence: The full sequence of sounds.
    :type sequence: list[list[Sound]]
    :param i1: The index of the first syllable in the subsequence of
    sounds being considered. 0 refers to the first syllable in a sequence.
    :type i1: int
    :param j1: The index of the first Sound in the subsequence being
    considered within its syllable. 0 refers to the first Sound in a
    syllable.
    :type j1: int
    :param i2: The index of the last syllable in the subsequence of sounds
    being considered.
    :type i2: int
    :param j2: The index of the last Sound in the subsequence being
    considered within its syllable.
    :type j2: int
    :param condition: The condition to evaluate.
    :type condition: str
    :param condition_sounds: Any sounds that are be part of the condition
    as specified by the '@' character in the condition. For example, the
    condition '@_@' matches on sounds that are in between two specified
    sounds, and those specified sounds are defined in this parameter in
    order. So, [Sound('s'), Sound('b')] for this parameter would cause a
    match on any sounds in between the sounds represented by 's' and 'b'.
    Can be None if there are no specific sounds in the condition.
    :type condition_sounds: list[Sound]
    :return: Whether the condition is matched by the specified Sound or
    subsequence of sounds.
    :rtype: bool
    """
    assert '_' in condition
    if '@' in condition:
        assert type(condition_sounds) is list and len(condition_sounds) >= condition.count('@')
    conditions_met = True
    sound_position = condition.index('_')
    condition_sounds_used = 0
    k = 0
    while k < len(condition) and conditions_met:
        if k != sound_position:
            inverted = condition[k] == '!'
            if k < sound_position:
                if inverted:
                    k = k + 1  # negation preceding _: check position relative to character that is negated
                target_sound = get_nearby_sound(sequence, i1, j1, k - sound_position)
            else:
                target_sound = get_nearby_sound(sequence, i2, j2, k - sound_position)
                if inverted:
                    k = k + 1  # negation following _: check position relative to !, then advance
            if condition[k] == '@':  # @ here tells the code to check against the next sound in condition_sounds
                if (not inverted and condition_sounds[condition_sounds_used] != target_sound) or \
                        (inverted and condition_sounds[condition_sounds_used] == target_sound):
                    conditions_met = False
                condition_sounds_used = condition_sounds_used + 1
            else:  # anything other than @, _, and ! assumed to be a word category (# is handled in get_nearby_sound)
                if (not inverted and condition[k] not in target_sound.phonotactics_categories) or \
                   (inverted and condition[k] in target_sound.phonotactics_categories):
                    conditions_met = False
        k = k + 1
    return conditions_met


def change_sounds(sequence: 'list[list[Sound]]', sounds_before: 'Sound | list[Sound] | None | str | list[str]',
                  sounds_after: 'Sound | list[Sound] | None', condition: str = '',
                  condition_sounds: 'list[Sound] | None' = None) -> 'list[list[Sound]]':
    """Convert sounds in a sequence into other sounds.

    All occurrences of sounds_before in the sequence that match the
    provided condition will be replaced with sounds_after.

    :param sequence: The sequence of sounds.
    :type sequence: list[list[Sound]]
    :param sounds_before: The Sound, sequence of sounds, category of
    Sound, or sequence of categories to convert into something else.
    :type sounds_before: Sound | list[Sound] | str | list[str]
    :param sounds_after: The Sound or sequence of sounds to replace
    sounds_before with. Can also be None to simply remove sounds_before.
    :type sounds_after: Sound | list[Sound]
    :param condition: The condition to check sounds_before against before
    replacing it. For example, '_#' will cause sounds_before to only be
    replaced at the end of a sequence as opposed to every time it occurs
    in the sequence.
    :type condition: str
    :param condition_sounds: Any sounds that are be part of the condition
    as specified by the '@' character in the condition. For example, the
    condition '@_@' matches on sounds that are in between two specified
    sounds, and those specified sounds are defined in this parameter in
    order. So, [Sound('s'), Sound('b')] for this parameter would cause a
    match on any sounds in between the sounds represented by 's' and 'b'.
    Can be None if there are no specific sounds in the condition.
    :type condition_sounds: list[Sound]
    :return: The converted sequence.
    :rtype: list[list[Sound]]
    """
    # print('changing sound', get_sequence_as_string(sequence), 'from', get_sequence_as_string([sounds_before]), 'to',
    #       get_sequence_as_string([sounds_after]))
    if type(sounds_before) is not list:
        sounds_before = [sounds_before]
    if type(sounds_after) is not list:
        sounds_after = [sounds_after]
    if len(sounds_after) == 1 and sounds_after[0] is None:
        sounds_after = None
    new_stem = list()
    i = 0
    j = 0
    match_count = 0
    match_locations = list()
    match_sounds = list()
    none_target = None
    while i < len(sequence):
        new_syllable = list()
        while j < len(sequence[i]):
            while match_count < len(sounds_before) and sounds_before[match_count] is None:  # match all None sounds
                match_count = match_count + 1
                match_locations.append((i, j))
                match_sounds.append(None)
                none_target = copy.deepcopy(sequence[i][j])
            if match_count < len(sounds_before):  # check for a match of one non-None sound
                if (type(sounds_before[match_count]) is Sound and
                        sequence[i][j].orthographic_transcription ==
                        sounds_before[match_count].orthographic_transcription) or \
                        (type(sounds_before[match_count]) is str and
                         sounds_before[match_count] in sequence[i][j].phonotactics_categories):  # one sound matched
                    match_count = match_count + 1
                    match_locations.append((i, j))
                    match_sounds.append(copy.deepcopy(sequence[i][j]))
                    none_target = None
                else:  # match failed: put the old sounds back and undo the match
                    for (match_i, match_j), match_sound in zip(match_locations, match_sounds):
                        if match_sound is not None:
                            if match_i < i:
                                new_stem[match_i].append(copy.deepcopy(match_sound))
                            else:
                                new_syllable.append(copy.deepcopy(match_sound))
                    new_syllable.append(copy.deepcopy(sequence[i][j]))
                    match_count = 0
                    match_locations = list()
                    match_sounds = list()
            if match_count >= len(sounds_before):  # full match found
                if not condition:  # no condition specified: replace sounds automatically
                    if sounds_after is not None:
                        new_syllable += copy.deepcopy(sounds_after)
                    match_count = 0
                    match_locations = list()
                    match_sounds = list()
                else:  # condition specified: check condition before replacing sounds
                    match_i, match_j = match_locations[0]
                    last_i, last_j = i, j
                    if match_sounds[-1] is None:
                        last_j = last_j - 1
                        if last_j < 0 < last_i:
                            last_i = last_i - 1
                            last_j = 0
                    if check_condition(sequence, match_i, match_j, last_i, last_j, condition, condition_sounds):
                        if sounds_after is not None:  # (^1)condition passed: replace sounds
                            new_syllable += copy.deepcopy(sounds_after)
                        match_count = 0
                        match_locations = list()
                        match_sounds = list()
                    else:  # condition failed: put the old sounds back and undo the match
                        for (match_i, match_j), match_sound in zip(match_locations, match_sounds):
                            if match_sound is not None:
                                if match_i < i:
                                    new_stem[match_i].append(copy.deepcopy(match_sound))
                                else:
                                    new_syllable.append(copy.deepcopy(match_sound))
                        match_count = 0
                        match_locations = list()
                        match_sounds = list()
                if none_target is not None:  # TODO does this always preserve syllable bounds?
                    new_syllable.append(none_target)
            j += 1
        new_stem.append(new_syllable)
        i += 1
        j = 0
    while match_count < len(sounds_before) and sounds_before[match_count] is None:  # match all None sounds once more
        match_count = match_count + 1
        match_locations.append((len(sequence)-1, len(sequence[-1])))
        match_sounds.append(None)
    if match_count >= len(sounds_before):  # full match found (special case; None can match after the sequence)
        if not condition:  # no condition specified: replace sounds automatically
            if sounds_after is not None:
                new_stem[-1] += copy.deepcopy(sounds_after)
                match_locations = list()
                match_sounds = list()
        else:  # condition specified: check condition before replacing sounds
            match_i, match_j = match_locations[0]
            last_i, last_j = match_locations[-1]
            if match_sounds[-1] is None:
                last_j = last_j - 1
                if last_j < 0 < last_i:
                    last_i = last_i - 1
                    last_j = 0
            if check_condition(sequence, match_i, match_j, last_i, last_j, condition, condition_sounds):
                if sounds_after is not None:  # (^1)condition passed: replace sounds
                    new_stem[-1] += copy.deepcopy(sounds_after)
                match_locations = list()
                match_sounds = list()
    for (match_i, match_j), match_sound in zip(match_locations, match_sounds):
        if match_sound is not None:  # (^1)put old sounds back in case of partial match
            new_stem[match_i].append(copy.deepcopy(match_sound))
    return new_stem


def get_sequence_as_string(sequence: 'list[list[Sound]]', use_ipa: bool = False) -> str:
    """Return a string representation of a sequence of sounds.

    For example, "[[Sound('h'), Sound('e'), Sound('l')], [Sound('l'),
    Sound('o')]]" will return "hello".

    :param sequence: The sequence of sounds.
    :type sequence: list[list[Sound]]
    :param use_ipa: Whether to use the IPA representation of each Sound
    instead of its orthographic transcription.
    :type use_ipa: bool
    :return: A string representation of a sequence of sounds.
    :rtype: str
    """
    output = ''
    for syllable in sequence:
        if syllable is not None:
            for sound in syllable:
                if sound is not None:
                    if not use_ipa:
                        output = output + sound.orthographic_transcription
                    else:
                        output = output + sound.ipa_transcription
    return output
