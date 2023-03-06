import unittest
from copy import copy

from conarch.language import Language
from conarch.sound import Sound
from conarch.sound_change_rule import SoundChangeRule
from conarch.sound_helpers import change_sounds
from conarch.word import Word


# noinspection SpellCheckingInspection
class TestSoundHelpers(unittest.TestCase):
    def test_change_sounds_1(self):
        """
        Test a single basic sound change.

        'a' to 'b' via 'a > b'
        """
        a = Sound('a')
        b = Sound('b')
        old_sequence = [[a]]
        target_sequence = [[b]]
        new_sequence = change_sounds(old_sequence, [a], [b])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_2(self):
        """
        Test that when a sequence contains two instances of sounds to
        change, both will be changed with a single call to change_sounds.

        'aa' to 'bb' via 'a > b'
        """
        a = Sound('a')
        b = Sound('b')
        old_sequence = [[a, a]]
        target_sequence = [[b, b]]
        new_sequence = change_sounds(old_sequence, [a], [b])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_3(self):
        """
        Test that a sound change can convert a single sound into multiple
        different sounds.

        'a' to 'bc' via 'a > bc'
        """
        a = Sound('a')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[a]]
        target_sequence = [[b, c]]
        new_sequence = change_sounds(old_sequence, [a], [b, c])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_4(self):
        """
        Test that a sound change can convert multiple different sounds
        into a single sound.

        'ab' to 'c' via 'ab > c'
        """
        a = Sound('a')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[a, b]]
        target_sequence = [[c]]
        new_sequence = change_sounds(old_sequence, [a, b], [c])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_5(self):
        """
        Test that a sound change can "extend" one sound to multiple
        copies of itself.

        'a' to 'aa' via 'a > aa'
        """
        a = Sound('a')
        old_sequence = [[a]]
        target_sequence = [[a, a]]
        new_sequence = change_sounds(old_sequence, [a], [a, a])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_6(self):
        """
        Test that a sound change can "contract" multiple instances of
        the same sound to a single instance.

        'aa' to 'a' via 'aa > a'
        """
        a = Sound('a')
        old_sequence = [[a, a]]
        target_sequence = [[a]]
        new_sequence = change_sounds(old_sequence, [a, a], [a])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_7(self):
        """
        Test that the condition '#_' will cause only sounds at the
        beginning of a sequence to be changed.

        'aa' to 'bca' via 'a > bc /#_'
        """
        a = Sound('a')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[a, a]]
        target_sequence = [[b, c, a]]
        new_sequence = change_sounds(old_sequence, [a], [b, c], condition='#_')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_8(self):
        """
        Test that the condition '_#' will cause only sounds at the end
        of a sequence to be changed.

        'aa' to 'abc' via 'a > bc /_#'
        """
        a = Sound('a')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[a, a]]
        target_sequence = [[a, b, c]]
        new_sequence = change_sounds(old_sequence, [a], [b, c], condition='_#')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_9(self):
        """
        Test that the condition 'V_' will cause only sounds following a
        vowel to be changed.

        'babb' to 'bacb' via 'b > c /V_'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[b, a, b, b]]
        target_sequence = [[b, a, c, b]]
        new_sequence = change_sounds(old_sequence, [b], [c], condition='V_')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_10(self):
        """
        Test that the condition '_V' will cause only sounds preceding a
        vowel to be changed.

        'bbab' to 'bcab' via 'b > c /_V'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[b, b, a, b]]
        target_sequence = [[b, c, a, b]]
        new_sequence = change_sounds(old_sequence, [b], [c], condition='_V')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_11(self):
        """
        Test that the condition 'V_C' will cause only sounds following a
        vowel and preceding a consonant to be changed.

        'abcba' to 'abacba' via 'b > ba /V_C'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, c, b, a]]
        target_sequence = [[a, b, a, c, b, a]]
        new_sequence = change_sounds(old_sequence, [b], [b, a], condition='V_C')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_12(self):
        """
        Test that the condition 'V_V' will cause a group of sounds in
        between vowels to change.

        'abcba' to 'aaa' via 'bcb > a /V_V'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, c, b, a]]
        target_sequence = [[a, a, a]]
        new_sequence = change_sounds(old_sequence, [b, c, b], [a], condition='V_V')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_13(self):
        """
        Test that the condition '#_#' will cause entire sequences that
        match the specified sounds to change.

        'ab' to 'c' via 'ab > c /#_#'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[c]]
        new_sequence = change_sounds(old_sequence, [a, b], [c], condition='#_#')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_14(self):
        """
        Test that the condition '#_#' will cause sequences that do not
        match the specified sounds entirely to remain the same.

        'abab' to 'abab' via 'ab > c /#_#'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, a, b]]
        target_sequence = [[a, b, a, b]]
        new_sequence = change_sounds(old_sequence, [a, b], [c], condition='#_#')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_15(self):
        """
        Test that attempting to change a sound that is not present in a
        specified sequence will have no effect.

        'ab' to 'ab' via 'c > ab'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[a, b]]
        new_sequence = change_sounds(old_sequence, [c], [a, b])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_16(self):
        """
        Test including a sound in a condition.

        'abcb' to 'abbcb' via 'b > bb /a_'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, c, b]]
        target_sequence = [[a, b, b, c, b]]
        new_sequence = change_sounds(old_sequence, [b], [b, b], condition='@_', condition_sounds=[a])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_17(self):
        """
        Test including two sounds in a condition.

        'abcbab' to 'abbcbab' via 'b > bb /a_c'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, c, b, a, b]]
        target_sequence = [[a, b, b, c, b, a, b]]
        new_sequence = change_sounds(old_sequence, [b], [b, b], condition='@_@', condition_sounds=[a, c])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_18(self):
        """
        Test a condition that contains a combination of end-of-sequence
        markers, category markers, and specific sounds.

        'aabbccc' to 'aabbabccc' via 'b > bab /#VVb_Ccc#'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, a, b, b, c, c, c]]
        target_sequence = [[a, a, b, b, a, b, c, c, c]]
        new_sequence = change_sounds(old_sequence, [b], [b, a, b], condition='#VV@_C@@#', condition_sounds=[b, c, c])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_19(self):
        """
        Test a condition that contains a negation.

        'abbc' to 'aabc' via 'b > a /!C_'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, b, c]]
        target_sequence = [[a, a, b, c]]
        new_sequence = change_sounds(old_sequence, [b], [a], condition='!C_')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_20(self):
        """
        Test a condition that contains a negation following an underscore.

        'cbba' to 'cbaa' via 'b > a /_!C'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[c, b, b, a]]
        target_sequence = [[c, b, a, a]]
        new_sequence = change_sounds(old_sequence, [b], [a], condition='_!C')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_21(self):
        """
        Test a basic sound change that passes a Sound for sounds_before and
        sounds_after instead of a List of one Sound each.

        'ab' to 'aa' via 'b > a'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[a, a]]
        new_sequence = change_sounds(old_sequence, b, a)
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_22(self):
        """
        Test changing a sound into nothing.

        'ab' to 'a' via 'b > Ø'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[a]]
        new_sequence = change_sounds(old_sequence, b, None)
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_23(self):
        """
        Test changing multiple sounds into nothing.

        'abc' to 'a' via 'bc > Ø'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, c]]
        target_sequence = [[a]]
        new_sequence = change_sounds(old_sequence, [b, c], None)
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_24(self):
        """
        Test changing every sound in a sequence into nothing.

        'abc' to 'Ø' via 'abc > Ø'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, c]]
        target_sequence = [[]]
        new_sequence = change_sounds(old_sequence, [a, b, c], None)
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_25(self):
        """
        Test a "suffix" type sound change that adds a Sound to the end of a
        sequence.

        'ab' to 'abc' via 'Ø > c /_#'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[a, b, c]]
        new_sequence = change_sounds(old_sequence, None, [c], condition='_#')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_26(self):
        """
        Test a "prefix" type sound change that adds a Sound to the beginning
        of a sequence.

        'ab' to 'cab' via 'Ø > c /#_'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[c, a, b]]
        new_sequence = change_sounds(old_sequence, None, [c], condition='#_')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_27(self):
        """
        Test an "infix" type sound change that inserts a Sound into the middle
        of a sequence based on a specific condition.

        'ab' to 'acb' via 'Ø > c /V_C'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[a, c, b]]
        new_sequence = change_sounds(old_sequence, None, [c], condition='V_C')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_28(self):
        """
        Test inserting a Sound in between every other Sound in a sequence,
        as well as at the beginning and end, by setting sounds_before to None
        and not specifying a condition.

        'aba' to 'cacbcac' via 'Ø > c'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, a]]
        target_sequence = [[c, a, c, b, c, a, c]]
        new_sequence = change_sounds(old_sequence, None, [c])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_29(self):
        """
        Test inserting a sequence of two sounds in between every other Sound
        in a sequence,  as well as at the beginning and end, by setting
        sounds_before to None and not specifying a condition.

        'aba' to 'cdacdbcdacd' via 'Ø > c'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        d = Sound('d', phonotactics_categories='C')
        old_sequence = [[a, b, a]]
        target_sequence = [[c, d, a, c, d, b, c, d, a, c,  d]]
        new_sequence = change_sounds(old_sequence, None, [c, d])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_30(self):
        """
        Test an "infix" type sound change that inserts a sequence of two
        sounds into the middle of a sequence based on a specific
        condition.

        'ab' to 'acdb' via 'Ø > cd /V_C'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        d = Sound('d', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[a, c, d, b]]
        new_sequence = change_sounds(old_sequence, None, [c, d], condition='V_C')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_31(self):
        """
        Test a "prefix" type sound change that adds a sequence of two sounds
        to the beginning of a sequence.

        'ab' to 'cdab' via 'Ø > cd /#_'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        d = Sound('d', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[c, d, a, b]]
        new_sequence = change_sounds(old_sequence, None, [c, d], condition='#_')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_32(self):
        """
        Test a "suffix" type sound change that adds a sequence of two sounds
        to the end of a sequence.

        'ab' to 'abcd' via 'Ø > cd /_#'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        d = Sound('d', phonotactics_categories='C')
        old_sequence = [[a, b]]
        target_sequence = [[a, b, c, d]]
        new_sequence = change_sounds(old_sequence, None, [c, d], condition='_#')
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_33(self):
        """
        Test a sound change that converts multiple sounds into something and
        contains subsequences of partial matches for the target sounds as well
        as a full match.

        'abaabaaab' to 'abaabcb' via 'aaa > c'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[a, b, a, a, b, a, a, a, b]]
        target_sequence = [[a, b, a, a, b, c, b]]
        new_sequence = change_sounds(old_sequence, [a, a, a], [c])
        self.assertEqual(target_sequence, new_sequence)

    def test_change_sounds_34(self):
        """
        Test a sound change that converts multiple sounds into something and
        contains a subsequence of partial matches for the target sounds at the
        end of the sequence as well as a full match.

        'baaabaa' to 'bcbaa' via 'aaa > c'
        """
        a = Sound('a', phonotactics_categories='V')
        b = Sound('b', phonotactics_categories='C')
        c = Sound('c', phonotactics_categories='C')
        old_sequence = [[b, a, a, a, b, a, a]]
        target_sequence = [[b, c, b, a, a]]
        new_sequence = change_sounds(old_sequence, [a, a, a], [c])
        self.assertEqual(target_sequence, new_sequence)


# noinspection SpellCheckingInspection
class TestWord(unittest.TestCase):
    def setUp(self):
        self.a_ae = Sound('a', 'æ', 'V')
        self.b = Sound('b', 'b', 'C')
        self.a_schwa = Sound('a', 'ə', 'Və')
        self.c_k = Sound('c', 'k', 'C')
        self.u_schwa = Sound('u', 'ə', 'Və')
        self.s = Sound('s', 's', 'C')
        self.abacus = Word([[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u_schwa, self.s]], 'N',
                           assign_id=False)  # don't use id assignment for tests not specifically about id assignment
        self.u = Sound('u', 'u', 'V')
        self.unschwa_u = SoundChangeRule(self.u_schwa, self.u)
        self.schwa_u = SoundChangeRule(self.u, self.u_schwa)
        self.p = Sound('p', 'p', 'C')
        self.unvoice_b = SoundChangeRule(self.b, self.p)
        self.d = Sound('d', 'd', 'C')
        self.puh_to_duh = SoundChangeRule(self.p, self.d, condition='_ə')
        self.t = Sound('t', 't', 'C')
        self.final_s_to_t = SoundChangeRule(self.s, self.t, condition='_#')
        self.voice_t = SoundChangeRule(self.t, self.d)
        self.stop = Sound("'", 'ʔ', 'C')
        self.final_d_to_stop = SoundChangeRule(self.d, self.stop, condition='_#')

    def test_word_1(self):
        """
        Test that a language sound change applies to the modern stem.
        """
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u, self.s]])

    def test_word_2(self):
        """
        Test that a language sound change does not apply to the base stem.
        """
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.assertEqual(self.abacus.get_base_stem(),
                         [[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u_schwa, self.s]])

    def test_word_3(self):
        """
        Test that a word sound change applies to the modern stem.
        """
        self.abacus.add_word_sound_change(self.unschwa_u)
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u, self.s]])

    def test_word_4(self):
        """
        Test that a word sound change does not apply to the base stem.
        """
        self.abacus.add_word_sound_change(self.unschwa_u)
        self.assertEqual(self.abacus.get_base_stem(),
                         [[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u_schwa, self.s]])

    def test_word_5(self):
        """
        Test that applying a language sound change twice will have the same
        effect as applying it once.
        """
        single = copy(self.abacus)
        double = copy(self.abacus)
        single.add_language_sound_change(self.unschwa_u)
        double.add_language_sound_change(self.unschwa_u)
        double.add_language_sound_change(self.unschwa_u)
        self.assertEqual(single.get_modern_stem(), double.get_modern_stem())

    def test_word_6(self):
        """
        Test that applying a word sound change twice will have the same
        effect as applying it once.
        """
        single = copy(self.abacus)
        double = copy(self.abacus)
        single.add_word_sound_change(self.unschwa_u)
        double.add_word_sound_change(self.unschwa_u)
        double.add_word_sound_change(self.unschwa_u)
        self.assertEqual(single.get_modern_stem(), double.get_modern_stem())

    def test_word_7(self):
        """
        Test that applying a sound change as a language sound change and
        again as a word sound change will have the same effect as applying
        it as only a language sound change.
        """
        single = copy(self.abacus)
        double = copy(self.abacus)
        single.add_language_sound_change(self.unschwa_u)
        double.add_language_sound_change(self.unschwa_u)
        double.add_word_sound_change(self.unschwa_u)
        self.assertEqual(single.get_modern_stem(), double.get_modern_stem())

    def test_word_8(self):
        """
        Test that applying a sound change as a language sound change and
        again as a word sound change will have the same effect as applying
        it as only a word sound change.
        """
        single = copy(self.abacus)
        double = copy(self.abacus)
        single.add_word_sound_change(self.unschwa_u)
        double.add_language_sound_change(self.unschwa_u)
        double.add_word_sound_change(self.unschwa_u)
        self.assertEqual(single.get_modern_stem(), double.get_modern_stem())

    def test_word_9(self):
        """
        Test that two different language sound changes both apply.
        """
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.abacus.add_language_sound_change(self.unvoice_b)
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.p, self.a_schwa], [self.c_k, self.u, self.s]])

    def test_word_10(self):
        """
        Test that two different word sound changes both apply.
        """
        self.abacus.add_word_sound_change(self.unschwa_u)
        self.abacus.add_word_sound_change(self.unvoice_b)
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.p, self.a_schwa], [self.c_k, self.u, self.s]])

    def test_word_11(self):
        """
        Test that two different sound changes, one a language sound change
        and one a word sound change, both apply.
        """
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.abacus.add_word_sound_change(self.unvoice_b)
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.p, self.a_schwa], [self.c_k, self.u, self.s]])

    def test_word_12(self):
        """
        Test that language sound changes apply in order by testing that a
        sound change dependent on a prior sound change applies.
        """
        self.abacus.add_language_sound_change(self.unvoice_b)
        self.abacus.add_language_sound_change(self.puh_to_duh)
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.d, self.a_schwa], [self.c_k, self.u_schwa, self.s]])

    def test_word_13(self):
        """
        Test that word sound changes apply in order by testing that a
        sound change dependent on a prior sound change applies.
        """
        self.abacus.add_word_sound_change(self.unvoice_b)
        self.abacus.add_word_sound_change(self.puh_to_duh)
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.d, self.a_schwa], [self.c_k, self.u_schwa, self.s]])

    def test_word_14(self):
        """
        Test that a mixture of word sound changes and language sound
        changes apply in order by testing that sound changes dependent
        on prior sound changes apply.
        """
        self.abacus.add_word_sound_change(self.unvoice_b)
        self.abacus.add_language_sound_change(self.puh_to_duh)
        self.abacus.add_language_sound_change(self.final_s_to_t)
        self.abacus.add_word_sound_change(self.voice_t)
        self.abacus.add_language_sound_change(self.final_d_to_stop)
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.d, self.a_schwa], [self.c_k, self.u_schwa, self.stop]])

    def test_word_15(self):
        """
        Test that language sound changes from before a word's original
        language stage do not apply.
        """
        self.abacus.add_language_sound_change(self.unvoice_b)  # stage 0 to 1
        self.abacus.add_language_sound_change(self.final_s_to_t)  # stage 1 to 2
        self.abacus.add_language_sound_change(self.unschwa_u)  # stage 2 to 3
        self.abacus.original_language_stage = 2  # added during stage 2, so the 0 to 2 changes should not apply
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u, self.s]])

    def test_word_16(self):
        """
        Test that language sound changes from after a word's obsoleted
        language stage do not apply.
        """
        self.abacus.add_language_sound_change(self.unvoice_b)  # stage 0 to 1
        self.abacus.add_language_sound_change(self.final_s_to_t)  # stage 1 to 2
        self.abacus.add_language_sound_change(self.unschwa_u)  # stage 2 to 3
        self.abacus.obsoleted_language_stage = 2  # obsoleted during stage 2, so the 2 to 3 change should not apply
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.p, self.a_schwa], [self.c_k, self.u_schwa, self.t]])

    def test_word_17(self):
        """
        Test that language sound changes from before a word's original
        language stage and after a word's obsoleted language stage both do
        not apply.
        """
        self.abacus.add_language_sound_change(self.unvoice_b)  # stage 0 to 1
        self.abacus.add_language_sound_change(self.final_s_to_t)  # stage 1 to 2
        self.abacus.add_language_sound_change(self.unschwa_u)  # stage 2 to 3
        self.abacus.original_language_stage = 1  # added during stage 1, so the 0 to 1 change should not apply
        self.abacus.obsoleted_language_stage = 2  # obsoleted during stage 2, so the 2 to 3 change should not apply
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u_schwa, self.t]])

    def test_word_18(self):
        """
        Test that a word with an original language stage equivalent to its
        obsoleted language stage will not have any language sound changes
        applied to it.
        """
        self.abacus.add_language_sound_change(self.unvoice_b)  # stage 0 to 1
        self.abacus.add_language_sound_change(self.final_s_to_t)  # stage 1 to 2
        self.abacus.add_language_sound_change(self.unschwa_u)  # stage 2 to 3
        self.abacus.original_language_stage = 2  # added during stage 1, so the 0 to 2 changes should not apply
        self.abacus.obsoleted_language_stage = 2  # obsoleted during stage 2, so the 2 to 3 change should not apply
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u_schwa, self.s]])

    def test_word_19(self):
        """
        Test that word sound changes from the word's original language stage
        apply to the word alongside the proper language sound changes.
        """
        self.abacus.add_language_sound_change(self.unvoice_b)  # stage 0 to 1
        self.abacus.add_word_sound_change(self.final_s_to_t)  # stage 1
        self.abacus.add_language_sound_change(self.unschwa_u)  # stage 1 to 2
        self.abacus.original_language_stage = 1  # added during stage 1, so the 0 to 1 change should not apply
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u, self.t]])

    def test_word_20(self):
        """
        Test that word sound changes from the word's obsoleted language stage
        apply to the word alongside the proper language sound changes.
        """
        self.abacus.add_language_sound_change(self.unvoice_b)  # stage 0 to 1
        self.abacus.add_word_sound_change(self.final_s_to_t)  # stage 1
        self.abacus.add_language_sound_change(self.unschwa_u)  # stage 1 to 2
        self.abacus.obsoleted_language_stage = 1  # obsoleted during stage 1, so the 1 to 2 change should not apply
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.p, self.a_schwa], [self.c_k, self.u_schwa, self.t]])

    def test_word_21(self):
        """
        Test that word sound changes from the word's only language stage
        apply to the word when its original language stage is equivalent to
        its obsoleted language stage alongside no language sound changes.
        """
        self.abacus.add_language_sound_change(self.unvoice_b)  # stage 0 to 1
        self.abacus.add_word_sound_change(self.final_s_to_t)  # stage 1
        self.abacus.add_language_sound_change(self.unschwa_u)  # stage 1 to 2
        self.abacus.original_language_stage = 1  # added during stage 1, so the 0 to 1 change should not apply
        self.abacus.obsoleted_language_stage = 1  # obsoleted during stage 1, so the 1 to 2 change should not apply
        self.assertEqual(self.abacus.get_modern_stem(),
                         [[self.a_ae], [self.b, self.a_schwa], [self.c_k, self.u_schwa, self.t]])

    def test_word_22(self):
        """
        Test that adding a definition to a Word causes it to be the definition
        for the current stage of the Word.
        """
        self.abacus.add_definition('A tool for performing calculations.', self.abacus.get_current_stage())
        self.assertEqual(self.abacus.get_definition_at_stage(self.abacus.get_current_stage()),
                         'A tool for performing calculations.')

    def test_word_23(self):
        """
        Test that a Word that has had no definitions added to it will not be
        considered defined at its current stage.
        """
        self.assertFalse(self.abacus.has_definition_at_stage(self.abacus.get_current_stage()))

    def test_word_24(self):
        """
        Test that a Word that has had one definition added to it will be
        considered defined at its current stage.
        """
        self.abacus.add_definition('A tool for performing calculations.', self.abacus.get_current_stage())
        self.assertTrue(self.abacus.has_definition_at_stage(self.abacus.get_current_stage()))

    def test_word_25(self):
        """
        Test that a Word that has definitions at multiple stages can access
        them properly by stage.
        """
        self.abacus.add_definition('A tool for performing calculations.', 0)
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.abacus.add_definition('An old tool for performing calculations.', 1)
        self.assertEqual(self.abacus.get_definition_at_stage(0), 'A tool for performing calculations.')
        self.assertEqual(self.abacus.get_definition_at_stage(1), 'An old tool for performing calculations.')

    def test_word_26(self):
        """
        Test that a Word that was defined at an older stage but not its most
        recent stage will use the previous definition for its most recent
        stage.
        """
        self.abacus.add_definition('A tool for performing calculations.', 0)
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.assertEqual(self.abacus.get_definition_at_stage(1), 'A tool for performing calculations.')

    def test_word_27(self):
        """
        Test that a Word that was defined at an older stage but not its most
        recent stage will return a blank definition when the definition is
        accessed by exact stage.
        """
        self.abacus.add_definition('A tool for performing calculations.', 0)
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.assertEqual(self.abacus.get_definition_at_stage(1, exact=True), '')

    def test_word_28(self):
        """
        Test that a Word that was defined at an older stage but not its most
        recent stage will not be considered defined when the definition is
        accessed by exact stage.
        """
        self.abacus.add_definition('A tool for performing calculations.', 0)
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.assertFalse(self.abacus.has_definition_at_stage(1, exact=True))

    def test_word_29(self):
        """
        Test that a Word that was defined at an older stage but not its most
        recent stage can determine the stage it was most recently defined at
        relative to its most recent stage.
        """
        self.abacus.add_definition('A tool for performing calculations.', 0)
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.assertEqual(self.abacus.get_definition_stage_at_stage(self.abacus.get_current_stage()), 0)

    def test_word_30(self):
        """
        Test that setting a Word as a form of another Word causes both words'
        base stems to be equal when there are no sound changes in either word.
        """
        dummy_form = Word([[]])
        self.abacus.add_form_word(dummy_form)
        self.assertEqual(self.abacus.get_base_stem(), dummy_form.get_base_stem())

    def test_word_31(self):
        """
        Test that setting a Word as a form of another Word that was added past
        the first language stage causes the form's base stem to be equal to
        the parent's stem at the stage the form was added.
        """
        self.abacus.add_language_sound_change(self.unschwa_u)
        dummy_form = Word([[]])
        self.abacus.add_form_word(dummy_form)
        self.assertEqual(self.abacus.get_stem_at_stage(1), dummy_form.get_base_stem())

    def test_word_32(self):
        """
        Test that the forms of a Word will inherit language sound changes that
        are added to the Word.
        """
        dummy_form = Word([[]])
        self.abacus.add_form_word(dummy_form)
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.assertIn(self.unschwa_u, dummy_form.language_sound_changes)

    def test_word_33(self):
        """
        Test that forms of a Word added after a language sound change will
        inherit the language sound change.
        """
        self.abacus.add_language_sound_change(self.unschwa_u)
        dummy_form = Word([[]])
        self.abacus.add_form_word(dummy_form)
        self.assertIn(self.unschwa_u, dummy_form.language_sound_changes)

    def test_word_34(self):
        """
        Test that forms of a Word added after a definition will have a
        definition at the same stage that contains the parent definition.
        """
        self.abacus.add_definition('A tool for performing calculations.', 0)
        dummy_form = Word([[]])
        self.abacus.add_form_word(dummy_form)
        self.assertTrue(dummy_form.has_definition_at_stage(0))
        self.assertIn('A tool for performing calculations.', dummy_form.get_definition_stage_at_stage(0))

    def test_word_35(self):
        """
        Test that forms of a Word added after two definitions will have
        definitions at the same stages that contain the parent definitions.
        """
        self.abacus.add_definition('A tool for performing calculations.', 0)
        self.abacus.add_language_sound_change(self.unschwa_u)
        self.abacus.add_definition('An old tool for performing calculations.', 1)
        dummy_form = Word([[]])
        self.abacus.add_form_word(dummy_form)
        self.assertTrue(dummy_form.has_definition_at_stage(0))
        self.assertIn('A tool for performing calculations.', dummy_form.get_definition_stage_at_stage(0))
        self.assertTrue(dummy_form.has_definition_at_stage(1))
        self.assertIn('An old tool for performing calculations.', dummy_form.get_definition_stage_at_stage(1))


# noinspection SpellCheckingInspection
class TestLanguage(unittest.TestCase):
    def setUp(self):
        # testspeak language and all its components
        self.t = Sound('t', 't', 'C')
        self.e = Sound('e', 'ɛ', 'V')
        self.s = Sound('s', 's', 'C')
        self.p = Sound('p', 'p', 'C')
        self.ea_i = Sound('ea', 'i', 'V')
        self.k = Sound('k', 'k', 'C')
        sounds = [self.t, self.e, self.s, self.p, self.ea_i, self.k]
        self.testspeak = Language('Testspeak', sounds, 'C(C)VC(C)')
        self.test = Word([[self.t, self.e, self.s, self.t]], 'N', assign_id=False)
        self.test.add_definition('Something that is done to confirm a desired behavior.', 0)
        self.test.word_id = 1
        self.speak = Word([[self.s, self.p, self.ea_i, self.k]], 'N', assign_id=False)
        self.test.add_definition('A suffix for the name of a language.', 0)
        self.speak.word_id = 2
        words = [self.test, self.speak]
        self.testspeak.add_words(words)

        # components that do not start as part of the testspeak language
        self.w = Sound('w', 'w', 'C')
        self.or_e = Sound('or', 'ɝ', 'V')
        self.d = Sound('d', 'd', 'C')
        self.word = Word([[self.w, self.or_e, self.d]], 'N', assign_id=False)
        self.final_st_to_s = SoundChangeRule([self.s, self.t], [self.s], condition='_#')
        self.unvoice_d = SoundChangeRule([self.d], [self.t])
        self.ee_i = Sound('ee', 'i', 'V')
        self.ch = Sound('ch', 't͡ʃ', 'C')
        self.speech = Word([[self.s, self.p, self.ee_i, self.ch]], assign_id=False)

    def test_language_1(self):
        """
        Test generation of a two-syllable Word of category 'N' (noun) from
        language stage 0.
        """
        word = self.testspeak.generate_word(min_syllable_length=2, max_syllable_length=2, category='N',
                                            language_stage=0, assign_id=False)
        word.word_id = 3
        self.assertIsInstance(word, Word)  # is a Word
        self.assertEqual(len(word.base_stem), 2)  # has 2 syllables
        for syllable in word.base_stem:
            for sound in syllable:
                self.assertIn(sound, self.testspeak.original_phonetic_inventory)  # contains only sounds from the lang
        self.assertTrue(word.fits_phonotactics(self.testspeak.phonotactics))  # matches language phonotactics

    def test_language_2(self):
        """
        Test that generating a Word from a Language and adding it to the
        Language will not cause the phonetic inventory of the Language to be
        modified from its original stage.
        """
        word = self.testspeak.generate_word(assign_id=False)
        self.testspeak.add_word(word)
        self.assertEqual(self.testspeak.original_phonetic_inventory, self.testspeak.modern_phonetic_inventory)

    def test_language_3(self):
        """
        Test that adding a Word to a Language with sounds not previously in
        the Language will cause those sounds to be added to its phonetic
        inventory based on the modern stem of the Word.
        """
        old_inventory = set(self.testspeak.modern_phonetic_inventory)
        self.testspeak.add_word(self.word)
        new_inventory = set(self.testspeak.modern_phonetic_inventory)
        target_inventory = set(self.word.get_modern_sounds()).union(old_inventory)
        self.assertNotEqual(old_inventory, new_inventory)
        self.assertEqual(target_inventory, new_inventory)

    def test_language_4(self):
        """
        Test generating 10 words at once and adding them all to the Language
        from which they were generated.
        """
        words = self.testspeak.generate_words(10, assign_ids=False)
        words_before = len(self.testspeak.words)
        self.testspeak.add_words(words)
        self.assertEqual(len(self.testspeak.words), words_before + 10)
        self.assertEqual(self.testspeak.original_phonetic_inventory, self.testspeak.modern_phonetic_inventory)

    def test_language_5(self):
        """
        Test that adding a sound change to a Language increments its current
        stage by 1.
        """
        stage_before = self.testspeak.get_current_stage()
        self.testspeak.apply_sound_change(self.final_st_to_s)
        self.assertEqual(self.testspeak.get_current_stage(), stage_before + 1)

    def test_language_6(self):
        """
        Test that adding a sound change to a Language causes it to be applied
        to all words in the Language.
        """
        self.testspeak.add_word(self.word)
        self.testspeak.apply_sound_change(self.unvoice_d)
        for word in self.testspeak.words:
            self.assertIn(self.unvoice_d, word.language_sound_changes)
        self.assertEqual(self.word.get_modern_stem(), [[self.w, self.or_e, self.t]])

    def test_language_7(self):
        """
        Test that adding a sound change to a Language causes it to be saved
        as the last item in the list of the language's sound changes.
        """
        self.testspeak.apply_sound_change(self.final_st_to_s)
        self.assertEqual(self.final_st_to_s, self.testspeak.sound_changes[-1])

    def test_language_8(self):
        """
        Test that adding a Word to a Language with a sound change will cause
        the Word to inherit the sound change from the Language even if the
        Word has been added at a stage where the sound change should not apply
        to it.
        """
        self.testspeak.apply_sound_change(self.unvoice_d)
        self.testspeak.add_word(self.word)
        self.assertIn(self.unvoice_d, self.word.language_sound_changes)  # the Word should contain the sound change
        self.assertNotIn(self.unvoice_d, self.word.all_sound_changes())  # but know not to apply it
        self.assertEqual(self.word.get_modern_stem(), [[self.w, self.or_e, self.d]])  # to the modern stem

    def test_language_9(self):
        """
        Test that adding alternating words and sound changes to a Language
        causes all words to inherit all sound changes in order.
        """
        self.testspeak.add_word(self.word)
        self.testspeak.apply_sound_change(self.unvoice_d)
        self.testspeak.add_word(self.speech)
        self.testspeak.apply_sound_change(self.final_st_to_s)
        for word in self.testspeak.words:
            for word_change, testspeak_change in zip(word.language_sound_changes, self.testspeak.sound_changes):
                self.assertEqual(word_change, testspeak_change)

    def test_language_10(self):
        """
        Test that adding alternating words and sound changes to a Language
        causes the added words to only apply sound changes to themselves that
        were added after they were.
        """
        self.testspeak.add_word(self.word)
        self.testspeak.apply_sound_change(self.unvoice_d)
        self.testspeak.add_word(self.speech)
        self.testspeak.apply_sound_change(self.final_st_to_s)
        self.assertIn(self.unvoice_d, self.word.all_sound_changes())
        self.assertIn(self.final_st_to_s, self.word.all_sound_changes())
        self.assertNotIn(self.unvoice_d, self.speech.all_sound_changes())
        self.assertIn(self.final_st_to_s, self.speech.all_sound_changes())

    def test_language_11(self):
        """
        Test that copying a Language at its most recent stage causes copies of
        every Word from the source Language (with the same base and modern
        stems, but not the same object) to be present in the copied Language.
        """
        cloned = self.testspeak.copy_language_at_stage()  # not specifying stage uses most recent
        self.assertEqual(len(self.testspeak.words), len(cloned.words))
        for source_word, cloned_word in zip(self.testspeak.words, cloned.words):
            self.assertEqual(source_word.get_base_stem_string(include_ipa=True),
                             cloned_word.get_base_stem_string(include_ipa=True))
            self.assertEqual(source_word.get_modern_stem_string(include_ipa=True),
                             cloned_word.get_modern_stem_string(include_ipa=True))
            self.assertNotEqual(source_word, cloned_word)

    def test_language_12(self):
        """
        Test that copied words in a copied Language maintain their original
        langauge stage, obsoleted language stage, and categories.
        """
        cloned = self.testspeak.copy_language_at_stage()  # not specifying stage uses most recent
        self.assertEqual(len(self.testspeak.words), len(cloned.words))
        for source_word, cloned_word in zip(self.testspeak.words, cloned.words):
            self.assertEqual(source_word.original_language_stage,
                             cloned_word.original_language_stage)
            self.assertEqual(source_word.obsoleted_language_stage,
                             cloned_word.obsoleted_language_stage)
            self.assertEqual(source_word.categories,
                             cloned_word.categories)

    def test_language_13(self):
        """
        Test that copied words in a copied Language maintain their definitions.
        """
        cloned = self.testspeak.copy_language_at_stage()  # not specifying stage uses most recent
        self.assertEqual(len(self.testspeak.words), len(cloned.words))
        for source_word, cloned_word in zip(self.testspeak.words, cloned.words):
            for (source_key, source_value), (cloned_key, cloned_value) in zip(source_word.get_definitions_and_stages(),
                                                                              cloned_word.get_definitions_and_stages()):
                self.assertEqual(source_key, cloned_key)
                self.assertEqual(source_value, cloned_value)

    def test_language_14(self):
        """
        Test that copied words in a copied Language maintain their language
        sound changes.
        """
        self.testspeak.apply_sound_change(self.unvoice_d)
        self.test.add_word_sound_change(self.final_st_to_s)
        cloned = self.testspeak.copy_language_at_stage()  # not specifying stage uses most recent
        self.assertEqual(len(self.testspeak.words), len(cloned.words))
        for source_word, cloned_word in zip(self.testspeak.words, cloned.words):
            self.assertEqual(len(source_word.language_sound_changes), len(cloned_word.language_sound_changes))
            for source_change, cloned_change in zip(source_word.language_sound_changes,
                                                    cloned_word.language_sound_changes):
                self.assertEqual(str(source_change), str(cloned_change))
                self.assertEqual(source_change.stage, cloned_change.stage)
                if source_change.condition_sounds is not None or cloned_change.condition_sounds is not None:
                    self.assertIsNotNone(source_change.condition_sounds)
                    self.assertIsNotNone(cloned_change.condition_sounds)
                    self.assertEqual(len(source_change.condition_sounds), len(cloned_change.condition_sounds))
                    for source_sound, cloned_sound in zip(source_change.condition_sounds, cloned_change.condition_sounds):
                        self.assertEqual(str(source_sound), str(cloned_sound))

    def test_language_15(self):
        """
        Test that copied words in a copied Language maintain their word sound
        changes.
        """
        self.testspeak.apply_sound_change(self.unvoice_d)
        self.test.add_word_sound_change(self.final_st_to_s)
        cloned = self.testspeak.copy_language_at_stage()  # not specifying stage uses most recent
        self.assertEqual(len(self.testspeak.words), len(cloned.words))
        for source_word, cloned_word in zip(self.testspeak.words, cloned.words):
            self.assertEqual(len(source_word.word_sound_changes), len(cloned_word.word_sound_changes))
            for source_change, cloned_change in zip(source_word.word_sound_changes,
                                                    cloned_word.word_sound_changes):
                self.assertEqual(str(source_change), str(cloned_change))
                self.assertEqual(source_change.stage, cloned_change.stage)
                if source_change.condition_sounds is not None or cloned_change.condition_sounds is not None:
                    self.assertIsNotNone(source_change.condition_sounds)
                    self.assertIsNotNone(cloned_change.condition_sounds)
                    self.assertEqual(len(source_change.condition_sounds), len(cloned_change.condition_sounds))
                    for source_sound, cloned_sound in zip(source_change.condition_sounds, cloned_change.condition_sounds):
                        self.assertEqual(str(source_sound), str(cloned_sound))

    def test_language_16(self):
        """
        Test that a copied Language maintains its name and phonotactics.
        """
        cloned = self.testspeak.copy_language_at_stage()  # not specifying stage uses most recent
        self.assertEqual(self.testspeak.name, cloned.name)
        self.assertEqual(self.testspeak.phonotactics, cloned.phonotactics)

    def test_language_17(self):
        """
        Test that a copied language's original phonetic inventory consists of
        sounds that are copies of sounds from the source language's original
        phonetic inventory.
        """
        cloned = self.testspeak.copy_language_at_stage()  # not specifying stage uses most recent
        self.assertEqual(len(self.testspeak.original_phonetic_inventory), len(cloned.original_phonetic_inventory))
        for original_sound, cloned_sound in zip(self.testspeak.original_phonetic_inventory,
                                                cloned.original_phonetic_inventory):
            self.assertIsNot(original_sound, cloned_sound)
            self.assertEqual(str(original_sound), str(cloned_sound))

    def test_language_18(self):
        """
        Test that copied words in a copied Language are made of sounds from
        the copied language's phonetic inventory.
        """
        cloned = self.testspeak.copy_language_at_stage()  # not specifying stage uses most recent
        inventory_sounds = [s for s in cloned.get_full_sound_inventory()]
        for word in cloned.words:
            for sound in word.get_modern_sounds():
                self.assertIn(sound, inventory_sounds)  # this might not be an accurate measurement b/c __eq__

    def test_language_19(self):
        """
        Test that copied words in a copied Language are made of sounds that
        are not in the original language's phonetic inventory.
        """
        cloned = self.testspeak.copy_language_at_stage()  # not specifying stage uses most recent
        inventory_sounds = [s for s in self.testspeak.get_full_sound_inventory()]
        for word in cloned.words:
            for sound in word.get_modern_sounds():
                for inventory_sound in inventory_sounds:
                    self.assertIsNot(sound, inventory_sound)  # assertNotIn does not apply here due to using __eq__


if __name__ == '__main__':
    unittest.main()
