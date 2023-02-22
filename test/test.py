import unittest
from copy import copy

from src.language import Language
from src.sound import Sound
from src.sound_change_rule import SoundChangeRule
from src.sound_helpers import change_sounds
from src.word import Word


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


# noinspection SpellCheckingInspection
class TestLanguage(unittest.TestCase):
    def setUp(self):
        self.t = Sound('t', 't', 'C')
        self.e = Sound('e', 'ɛ', 'V')
        self.s = Sound('s', 's', 'C')
        self.p = Sound('p', 'p', 'C')
        self.ea_i = Sound('ea', 'i', 'V')
        self.k = Sound('k', 'k', 'C')
        sounds = [self.t, self.e, self.s, self.p, self.ea_i, self.k]
        self.testspeak = Language('Testspeak', sounds, 'C(C)VC(C)')
        self.test = Word([[self.t, self.e, self.s, self.t]], 'N', assign_id=False)
        self.test.word_id = 1
        self.speak = Word([[self.s, self.p, self.ea_i, self.k]], 'N', assign_id=False)
        self.speak.word_id = 2
        words = [self.test, self.speak]
        self.testspeak.add_words(words)

    def test_language_1(self):
        """
        Test generation of a two-syllable Word of category 'N' (noun) from language stage 0.
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


if __name__ == '__main__':
    unittest.main()
