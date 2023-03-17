import copy
from conarch.sound import Sound


def get_nearby_sound(sequence: 'list[list[Sound]]', i: int, j: int, steps: int = 1, backwards: bool = False) -> Sound:
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
                  sounds_after: 'Sound | list[Sound] | None | str | list[str]', condition: str = '',
                  condition_sounds: 'list[Sound] | None' = None) -> 'list[list[Sound]]':
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
