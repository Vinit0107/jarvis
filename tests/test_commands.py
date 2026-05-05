import unittest
from unittest.mock import patch

from jarvis import Jarvis, clean_target_name, split_target_intent


class CommandParsingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jarvis = Jarvis(voice=False)
        self.jarvis.start_apps = {
            "netflix": {
                "name": "Netflix",
                "app_id": "4DF9E0F8.Netflix_mcm4njqhnhss8!Netflix.App",
            },
            "prime video": {
                "name": "Prime Video",
                "app_id": "AmazonVideo.PrimeVideo_pwbj9vvecjh7j!PWA",
            },
            "whatsapp": {
                "name": "WhatsApp",
                "app_id": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
            },
        }

    def test_app_phrases_resolve_to_apps(self) -> None:
        cases = {
            "open the netflix app": "open netflix",
            "open prime": "open prime video",
            "launch google chrome": "open chrome",
            "start vs code": "open vscode",
            "open whats app": "open whatsapp",
        }

        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(self.jarvis.to_canonical_command(command), expected)

    def test_website_phrases_resolve_to_websites(self) -> None:
        cases = {
            "open netflix website": "website netflix",
            "visit youtube": "website youtube",
            "go to gmail": "website gmail",
        }

        for command, expected in cases.items():
            with self.subTest(command=command):
                self.assertEqual(self.jarvis.to_canonical_command(command), expected)

    def test_questions_resolve_to_search(self) -> None:
        self.assertEqual(
            self.jarvis.to_canonical_command("what is python"),
            "search what is python",
        )
        self.assertEqual(
            self.jarvis.to_canonical_command("search web for iron man"),
            "search iron man",
        )

    def test_target_hint_cleanup(self) -> None:
        self.assertEqual(clean_target_name("the Netflix app"), "netflix")
        self.assertEqual(split_target_intent("Netflix website"), ("netflix", "website"))
        self.assertEqual(split_target_intent("Prime Video app"), ("prime video", "app"))


class RoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jarvis = Jarvis(voice=False)
        self.jarvis.start_apps = {
            "netflix": {
                "name": "Netflix",
                "app_id": "4DF9E0F8.Netflix_mcm4njqhnhss8!Netflix.App",
            }
        }

    def test_installed_app_routes_to_start_app(self) -> None:
        with patch.object(self.jarvis, "open_start_app", return_value=True) as opener:
            result = self.jarvis.open_target("netflix")

        opener.assert_called_once_with("4DF9E0F8.Netflix_mcm4njqhnhss8!Netflix.App")
        self.assertEqual(result, "Opening the Netflix app on your laptop.")

    def test_unknown_app_does_not_fall_back_to_browser_search(self) -> None:
        with patch("jarvis.webbrowser.open") as browser:
            result = self.jarvis.open_target("totally unknown app")

        browser.assert_not_called()
        self.assertIn("I did not open Chrome", result)


if __name__ == "__main__":
    unittest.main()
