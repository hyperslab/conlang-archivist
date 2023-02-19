import unittest
from src.sound import Sound
from src.sound_helpers import change_sounds


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


if __name__ == '__main__':
    unittest.main()
