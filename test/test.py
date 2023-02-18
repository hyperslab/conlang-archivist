import unittest
from src.sound import Sound
from src.sound_helpers import change_sounds


# noinspection SpellCheckingInspection
class TestSoundHelpers(unittest.TestCase):
    def test_change_sounds_1(self):
        """
        Test a single basic sound change.

        'a' to 'b'
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

        'aa' to 'bb'
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

        'a' to 'bc'
        """
        a = Sound('a')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[a]]
        target_sequence = [[b, c]]
        new_syllable = change_sounds(old_sequence, [a], [b, c])
        self.assertEqual(target_sequence, new_syllable)

    def test_change_sounds_4(self):
        """
        Test that a sound change can convert multiple different sounds
        into a single sound.

        'ab' to 'c'
        """
        a = Sound('a')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[a, b]]
        target_sequence = [[c]]
        new_syllable = change_sounds(old_sequence, [a, b], [c])
        self.assertEqual(target_sequence, new_syllable)

    def test_change_sounds_5(self):
        """
        Test that a sound change can "extend" one sound to multiple
        copies of itself.

        'a' to 'aa'
        """
        a = Sound('a')
        old_sequence = [[a]]
        target_sequence = [[a, a]]
        new_syllable = change_sounds(old_sequence, [a], [a, a])
        self.assertEqual(target_sequence, new_syllable)

    def test_change_sounds_6(self):
        """
        Test that a sound change can "contract" multiple instances of
        the same sound to a single instance.

        'aa' to 'a'
        """
        a = Sound('a')
        old_sequence = [[a, a]]
        target_sequence = [[a]]
        new_syllable = change_sounds(old_sequence, [a, a], [a])
        self.assertEqual(target_sequence, new_syllable)

    def test_change_sounds_7(self):
        """
        Test that the condition '#_' will cause only sounds at the
        beginning of a sequence to be changed.

        'aa' to 'bca'
        """
        a = Sound('a')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[a, a]]
        target_sequence = [[b, c, a]]
        new_syllable = change_sounds(old_sequence, [a], [b, c], condition='#_')
        self.assertEqual(target_sequence, new_syllable)

    def test_change_sounds_8(self):
        """
        Test that the condition '_#' will cause only sounds at the end
        of a sequence to be changed.

        'aa' to 'abc'
        """
        a = Sound('a')
        b = Sound('b')
        c = Sound('c')
        old_sequence = [[a, a]]
        target_sequence = [[a, b, c]]
        new_syllable = change_sounds(old_sequence, [a], [b, c], condition='_#')
        self.assertEqual(target_sequence, new_syllable)


if __name__ == '__main__':
    unittest.main()
