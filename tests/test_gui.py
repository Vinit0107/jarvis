import unittest

from jarvis import Jarvis
from jarvis_gui import SilentSpeaker, voice_command_from_guesses


class GuiCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jarvis = Jarvis(voice=False)

    def test_voice_guesses_accept_wake_word(self) -> None:
        self.assertEqual(
            voice_command_from_guesses(self.jarvis, ["Jarvis open chrome"]),
            "open chrome",
        )

    def test_voice_guesses_accept_direct_command(self) -> None:
        self.assertEqual(
            voice_command_from_guesses(self.jarvis, ["open chrome"]),
            "open chrome",
        )

    def test_voice_guesses_use_later_candidate(self) -> None:
        self.assertEqual(
            voice_command_from_guesses(self.jarvis, ["", "visit youtube"]),
            "website youtube",
        )

    def test_silent_speaker_does_not_raise(self) -> None:
        self.assertIsNone(SilentSpeaker().say("hello"))


if __name__ == "__main__":
    unittest.main()
