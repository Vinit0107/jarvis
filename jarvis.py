import argparse
import datetime as dt
import difflib
import json
import os
import platform
import random
import re
import shutil
import subprocess
import time
import webbrowser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
NOTES_DIR = BASE_DIR / "notes"
CONFIG_PATH = BASE_DIR / "jarvis_apps.json"
START_APPS_CACHE_PATH = BASE_DIR / "start_apps_cache.json"
START_APPS_CACHE_SECONDS = 60 * 60 * 12
WAKE_WORDS = ("hey jarvis", "ok jarvis", "okay jarvis", "jarvis")
EXIT_COMMANDS = {"exit", "quit", "shutdown", "stop listening", "goodbye"}
OPEN_VERBS = ("open", "launch", "start", "run", "bring up")
MEDIA_OPEN_VERBS = ("watch", "play")
WEBSITE_OPEN_VERBS = (
    "open website",
    "open site",
    "open web",
    "go to",
    "visit",
    "browse to",
)
SEARCH_VERBS = (
    "search the web for",
    "search web for",
    "search for",
    "search",
    "google",
    "look up",
    "find",
)
NOTE_VERBS = ("make a note", "take a note", "remember", "note")
SEARCH_QUESTION_PREFIXES = (
    "what is ",
    "who is ",
    "where is ",
    "when is ",
    "why is ",
    "why does ",
    "how to ",
    "how do i ",
    "tell me about ",
)
FILLER_PREFIXES = (
    "could you please ",
    "can you please ",
    "would you please ",
    "please ",
    "could you ",
    "can you ",
    "would you ",
    "will you ",
)
APP_HINT_WORDS = {"app", "application", "program", "software", "desktop app"}
WEBSITE_HINT_WORDS = {"website", "site", "web page", "online"}

APP_ALIASES = {
    "amazon prime": "prime video",
    "amazon prime video": "prime video",
    "amazon video": "prime video",
    "browser": "chrome",
    "calc": "calculator",
    "calculator": "calculator",
    "chrome": "chrome",
    "chrome browser": "chrome",
    "code": "vscode",
    "edge": "edge",
    "edge browser": "edge",
    "file explorer": "file explorer",
    "google chrome": "chrome",
    "microsoft edge": "edge",
    "music": "spotify",
    "net flex": "netflix",
    "net flix": "netflix",
    "netflix": "netflix",
    "netflix app": "netflix",
    "note pad": "notepad",
    "notepad": "notepad",
    "paint": "paint",
    "prime": "prime video",
    "prime video": "prime video",
    "prime videos": "prime video",
    "primevideo": "prime video",
    "settings": "settings",
    "spotify": "spotify",
    "task manager": "task manager",
    "terminal": "terminal",
    "visual studio code": "vscode",
    "vs code": "vscode",
    "v s code": "vscode",
    "vscode": "vscode",
    "whats app": "whatsapp",
    "whatsapp": "whatsapp",
    "windows explorer": "file explorer",
    "windows settings": "settings",
    "windows terminal": "terminal",
}

WEBSITE_ALIASES = {
    "amazon prime": "primevideo.com",
    "amazon prime video": "primevideo.com",
    "gmail": "mail.google.com",
    "google": "google.com",
    "netflix": "netflix.com",
    "prime": "primevideo.com",
    "prime video": "primevideo.com",
    "primevideo": "primevideo.com",
    "whatsapp": "web.whatsapp.com",
    "whatsapp web": "web.whatsapp.com",
    "you tube": "youtube.com",
    "youtube": "youtube.com",
}


DEFAULT_APPS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "edge": [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "msedge.exe",
    ],
    "file explorer": ["explorer.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "settings": ["ms-settings:"],
    "vscode": [
        r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "code",
    ],
    "task manager": ["taskmgr.exe"],
    "terminal": ["wt.exe"],
    "spotify": [
        r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
    ],
}


class Speaker:
    def __init__(self) -> None:
        self.engine = None
        try:
            import pyttsx3

            self.engine = pyttsx3.init()
        except Exception:
            self.engine = None

    def say(self, message: str) -> None:
        print(f"JARVIS: {message}")
        if self.engine:
            self.engine.say(message)
            self.engine.runAndWait()


class VoiceListener:
    def __init__(self, recognition: str = "offline") -> None:
        self.available = False
        self.error = ""
        self.recognition = recognition
        try:
            import speech_recognition as sr

            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.6
            self.recognizer.non_speaking_duration = 0.4
            self.recognizer.phrase_threshold = 0.25
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)

            if recognition == "offline":
                import pocketsphinx  # noqa: F401

            self.available = True
        except Exception as exc:
            self.error = str(exc)

    def listen(self) -> list[str]:
        if not self.available:
            return []

        print("Listening...")
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=10)
            if self.recognition == "offline":
                return self.recognize_offline(audio)
            if self.recognition == "auto":
                offline_guesses = self.recognize_offline(audio, quiet=True)
                if offline_guesses:
                    return offline_guesses
                return self.recognize_online(audio)
            return self.recognize_online(audio)
        except self.sr.WaitTimeoutError:
            return []

    def recognize_offline(self, audio, quiet: bool = False) -> list[str]:
        try:
            text = self.recognizer.recognize_sphinx(audio)
            if text:
                print(f"You: {text}")
                return [text]
            return []
        except self.sr.UnknownValueError:
            if not quiet:
                print("JARVIS: I heard something, but could not understand it.")
            return []
        except self.sr.RequestError as exc:
            if not quiet:
                print(f"JARVIS: Offline speech recognition is unavailable: {exc}")
            return []

    def recognize_online(self, audio) -> list[str]:
        try:
            response = self.recognizer.recognize_google(audio, show_all=True)
            alternatives = response.get("alternative", []) if isinstance(response, dict) else []
            guesses = [
                item["transcript"]
                for item in alternatives
                if isinstance(item, dict) and item.get("transcript")
            ]
            if guesses:
                print(f"You: {guesses[0]}")
            return guesses
        except self.sr.UnknownValueError:
            print("JARVIS: I heard something, but could not understand it.")
            return []
        except self.sr.RequestError as exc:
            print(f"JARVIS: Speech recognition is unavailable: {exc}")
            return []


class Jarvis:
    def __init__(self, voice: bool = False, recognition: str = "offline") -> None:
        self.speaker = Speaker()
        self.listener = VoiceListener(recognition=recognition) if voice else None
        self.notes_dir = NOTES_DIR
        self.notes_dir.mkdir(exist_ok=True)
        self.apps = self._load_apps()
        self.start_apps = self._load_start_apps()

    def _load_apps(self) -> dict[str, list[str]]:
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    merged = DEFAULT_APPS | data
                    if merged != data:
                        CONFIG_PATH.write_text(
                            json.dumps(merged, indent=2),
                            encoding="utf-8",
                        )
                    return merged
            except json.JSONDecodeError:
                pass
        CONFIG_PATH.write_text(
            json.dumps(DEFAULT_APPS, indent=2),
            encoding="utf-8",
        )
        return DEFAULT_APPS

    def _load_start_apps(self, force_refresh: bool = False) -> dict[str, dict[str, str]]:
        if platform.system() != "Windows":
            return {}

        if not force_refresh:
            cached_apps = self._read_start_apps_cache()
            if cached_apps is not None:
                return cached_apps

        command = (
            "Get-StartApps | "
            "Select-Object Name,AppID | "
            "ConvertTo-Json -Compress"
        )
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                capture_output=True,
                check=True,
                text=True,
                timeout=10,
            )
            raw_apps = json.loads(result.stdout) if result.stdout.strip() else []
        except Exception:
            return {}

        if isinstance(raw_apps, dict):
            raw_apps = [raw_apps]

        start_apps: dict[str, dict[str, str]] = {}
        for item in raw_apps:
            if not isinstance(item, dict):
                continue
            name = str(item.get("Name", "")).strip()
            app_id = str(item.get("AppID", "")).strip()
            if name and app_id:
                start_apps[normalize_text(name)] = {"name": name, "app_id": app_id}

        for alias, canonical in APP_ALIASES.items():
            canonical_key = normalize_text(canonical)
            if canonical_key in start_apps:
                start_apps[normalize_text(alias)] = start_apps[canonical_key]

        self._write_start_apps_cache(start_apps)
        return start_apps

    def _read_start_apps_cache(self) -> dict[str, dict[str, str]] | None:
        if not START_APPS_CACHE_PATH.exists():
            return None
        if time.time() - START_APPS_CACHE_PATH.stat().st_mtime > START_APPS_CACHE_SECONDS:
            return None

        try:
            data = json.loads(START_APPS_CACHE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

        if not isinstance(data, dict):
            return None
        return {
            str(key): {"name": str(value["name"]), "app_id": str(value["app_id"])}
            for key, value in data.items()
            if isinstance(value, dict) and "name" in value and "app_id" in value
        }

    def _write_start_apps_cache(self, start_apps: dict[str, dict[str, str]]) -> None:
        try:
            START_APPS_CACHE_PATH.write_text(
                json.dumps(start_apps, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def reply(self, message: str) -> str:
        self.speaker.say(message)
        return message

    def run(self) -> None:
        if self.listener:
            self.run_voice()
            return

        self.reply(
            "Online. I can open laptop apps. Try 'apps' to see shortcuts, or 'open chrome'."
        )
        while True:
            command = input("You: ").strip()
            if not command:
                continue
            result = self.handle(command)
            if result == "EXIT":
                break

    def run_voice(self) -> None:
        if not self.listener or not self.listener.available:
            detail = f" Details: {self.listener.error}" if self.listener else ""
            self.reply(f"Voice mode is not ready, so I am switching to text mode.{detail}")
            self.listener = None
            self.run()
            return

        mode = self.listener.recognition if self.listener else "voice"
        self.reply(
            f"{mode.capitalize()} voice mode online. I can open laptop apps. Say Jarvis open chrome, or Jarvis apps."
        )
        while True:
            guesses = self.listener.listen()
            if not guesses:
                continue

            command = self.best_voice_command(guesses)
            if not command:
                self.reply("Say Jarvis before the command so I know it is for me.")
                continue

            result = self.handle(command)
            if result == "EXIT":
                break

    def best_voice_command(self, guesses: list[str]) -> str:
        for guess in guesses:
            command = self.clean_voice_command(guess)
            if command:
                return self.to_canonical_command(command)
        return ""

    def clean_voice_command(self, command: str) -> str:
        lowered = command.lower().strip()
        if lowered in EXIT_COMMANDS:
            return lowered

        for wake_word in WAKE_WORDS:
            if lowered.startswith(wake_word):
                return command[len(wake_word) :].strip()

        jarvis_at = lowered.find("jarvis")
        if jarvis_at != -1:
            return command[jarvis_at + len("jarvis") :].strip()

        return ""

    def handle(self, command: str) -> str | None:
        command = self.to_canonical_command(command)
        lowered = normalize_text(command)

        if lowered in EXIT_COMMANDS:
            self.reply("Shutting down. See you soon.")
            return "EXIT"

        if lowered == "help":
            return self.reply(
                "I open installed laptop apps first. Try: apps, refresh apps, open Netflix, open Prime Video, launch Google Chrome, start VS Code, visit youtube.com, or search for Python tutorials."
            )

        if lowered in {"refresh apps", "rescan apps", "scan apps", "update apps"}:
            self.start_apps = self._load_start_apps(force_refresh=True)
            return self.reply(f"Updated the laptop app list. I found {len(self.start_apps)} app names and aliases.")

        if lowered in {"apps", "app list", "list apps", "show apps", "available apps"}:
            return self.reply(self.list_apps())

        if lowered in {"time", "what time is it", "tell me the time", "current time"}:
            return self.reply(dt.datetime.now().strftime("It is %I:%M %p."))

        if lowered in {"date", "what is the date", "today's date", "current date"}:
            return self.reply(dt.datetime.now().strftime("Today is %A, %d %B %Y."))

        if lowered in {"system", "system info", "pc info", "laptop info"}:
            return self.reply(self.get_system_info())

        if lowered.startswith("open "):
            target = command[5:].strip()
            return self.reply(self.open_target(target))

        if lowered.startswith("website "):
            target = command[8:].strip()
            return self.reply(self.open_website(resolve_website_target(target)))

        if lowered.startswith("search "):
            query = command[7:].strip()
            return self.reply(self.search_web(query))

        if lowered.startswith("note "):
            content = command[5:].strip()
            return self.reply(self.save_note(content))

        if lowered in {"list notes", "show notes"}:
            return self.reply(self.list_notes())

        if lowered.startswith("read note"):
            return self.reply(self.read_latest_note())

        if lowered in {"joke", "tell me a joke", "make me laugh"}:
            return self.reply(random.choice(JOKES))

        return self.reply(
            "I don't know that command yet. Type 'help' and I'll show you what I can do."
        )

    def get_system_info(self) -> str:
        return (
            f"You're running {platform.system()} {platform.release()} on "
            f"{platform.machine()} with Python {platform.python_version()}."
        )

    def to_canonical_command(self, command: str) -> str:
        cleaned = strip_filler(command)

        if cleaned in {"refresh apps", "rescan apps", "scan apps", "update apps"}:
            return "refresh apps"

        if cleaned in {"what time is it", "tell me the time", "current time"}:
            return "time"
        if cleaned in {"what is the date", "today's date", "current date"}:
            return "date"
        if cleaned in {"what apps can you open", "which apps can you open"}:
            return "apps"

        for verb in WEBSITE_OPEN_VERBS:
            prefix = f"{verb} "
            if cleaned.startswith(prefix):
                target = cleaned[len(prefix) :].strip()
                return f"website {clean_target_name(target)}"

        for verb in OPEN_VERBS + MEDIA_OPEN_VERBS:
            prefix = f"{verb} "
            if cleaned.startswith(prefix):
                target, intent = split_target_intent(cleaned[len(prefix) :].strip())
                if intent == "website":
                    return f"website {target}"
                return f"open {self.resolve_app_name(target)}"

        for verb in SEARCH_VERBS:
            prefix = f"{verb} "
            if cleaned.startswith(prefix):
                query = cleaned[len(prefix) :].strip()
                return f"search {query}"

        for prefix in SEARCH_QUESTION_PREFIXES:
            if cleaned.startswith(prefix):
                return f"search {cleaned}"

        for verb in NOTE_VERBS:
            prefix = f"{verb} "
            if cleaned.startswith(prefix):
                note = cleaned[len(prefix) :].strip()
                return f"note {note}"

        return cleaned

    def resolve_target_name(self, target: str) -> str:
        return self.resolve_app_name(target)

    def resolve_app_name(self, target: str) -> str:
        normalized = clean_target_name(target)
        if normalized in APP_ALIASES:
            return APP_ALIASES[normalized]
        if normalized in self.apps:
            return normalized
        if normalized in self.start_apps:
            return normalized

        choices = sorted(set(self.apps) | set(APP_ALIASES) | set(self.start_apps))
        close_matches = difflib.get_close_matches(normalized, choices, n=1, cutoff=0.76)
        if close_matches:
            return APP_ALIASES.get(close_matches[0], close_matches[0])

        return target.strip()

    def open_target(self, target: str) -> str:
        raw_target = target.strip()
        raw_lower = raw_target.lower().strip()
        raw_normalized = normalize_text(raw_target)

        if raw_lower.startswith(("http://", "https://")):
            return self.open_website(raw_target)

        target = self.resolve_app_name(target)
        target_lower = normalize_text(target)

        app_paths = self.apps.get(target_lower)
        if app_paths:
            for raw_path in app_paths:
                expanded = os.path.expandvars(raw_path)
                if expanded.lower().startswith(("ms-settings:", "shell:")):
                    os.startfile(expanded)
                    return f"Opening the {target} app on your laptop."
                if raw_path.endswith(".exe") and Path(expanded).exists():
                    os.startfile(expanded)
                    return f"Opening the {target} app on your laptop."
                if shutil.which(raw_path):
                    subprocess.Popen([raw_path], shell=False)
                    return f"Opening the {target} app on your laptop."
                try:
                    subprocess.Popen([expanded], shell=False)
                    return f"Opening the {target} app on your laptop."
                except OSError:
                    pass

        start_app = self.start_apps.get(target_lower)
        if start_app and self.open_start_app(start_app["app_id"]):
            return f"Opening the {start_app['name']} app on your laptop."

        if raw_normalized in WEBSITE_ALIASES and raw_normalized not in APP_ALIASES:
            return self.open_website(WEBSITE_ALIASES[raw_normalized])

        if looks_like_domain(raw_target):
            return self.open_website(raw_target)

        available = ", ".join(self.available_app_names())
        return (
            f"I could not find an installed app named {target}. "
            f"I did not open Chrome. Try 'apps' to see apps, or say 'visit {target}' if you want the website. "
            f"Known apps include: {available}."
        )

    def open_start_app(self, app_id: str) -> bool:
        try:
            if "://" in app_id:
                os.startfile(app_id)
            else:
                subprocess.Popen(
                    ["explorer.exe", f"shell:AppsFolder\\{app_id}"],
                    shell=False,
                )
            return True
        except OSError:
            return False

    def open_website(self, target: str) -> str:
        url = target.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        webbrowser.open(url)
        return f"Opening website {url}."

    def list_apps(self) -> str:
        app_names = ", ".join(self.available_app_names())
        featured = self.installed_app_examples()
        if featured:
            return (
                f"I can open these laptop app shortcuts: {app_names}. "
                f"I also found installed Windows apps like: {featured}. "
                "Say open, launch, or start followed by the app name."
            )
        return f"I can open these laptop app shortcuts: {app_names}. Say open, launch, or start followed by the app name."

    def installed_app_examples(self) -> str:
        preferred = [
            "netflix",
            "prime video",
            "whatsapp",
            "spotify",
            "discord",
            "camera",
            "calculator",
        ]
        names = []
        seen = set()
        for key in preferred:
            app = self.start_apps.get(key)
            if app and app["name"] not in seen:
                names.append(app["name"])
                seen.add(app["name"])
        return ", ".join(names[:5])

    def available_app_names(self) -> list[str]:
        names = set(self.apps)
        for key in ("netflix", "prime video", "whatsapp", "discord", "camera"):
            app = self.start_apps.get(key)
            if app:
                names.add(normalize_text(app["name"]))
        return sorted(names)

    def search_web(self, query: str) -> str:
        webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        return f"Searching the web for {query}."

    def save_note(self, content: str) -> str:
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        note_path = self.notes_dir / f"note_{timestamp}.txt"
        note_path.write_text(content, encoding="utf-8")
        return f"Saved note to {note_path.name}."

    def list_notes(self) -> str:
        notes = sorted(self.notes_dir.glob("note_*.txt"))
        if not notes:
            return "You do not have any notes yet."
        joined = ", ".join(note.name for note in notes[-5:])
        return f"Recent notes: {joined}."

    def read_latest_note(self) -> str:
        notes = sorted(self.notes_dir.glob("note_*.txt"))
        if not notes:
            return "You do not have any notes yet."
        latest = notes[-1]
        content = latest.read_text(encoding="utf-8").strip()
        return f"Your latest note says: {content}"


JOKES = [
    "I would tell you an engineering joke, but the build is still running.",
    "My favorite workout is running tasks in the background.",
    "I am not lazy. I am running in low-power standby.",
]


def normalize_text(value: str) -> str:
    normalized = value.lower().strip()
    normalized = re.sub(r"[^a-z0-9.+# ]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def clean_target_name(value: str) -> str:
    cleaned = strip_leading_articles(normalize_text(value))
    for hint in sorted(APP_HINT_WORDS | WEBSITE_HINT_WORDS, key=len, reverse=True):
        cleaned = remove_target_hint(cleaned, hint)
    return strip_leading_articles(cleaned)


def split_target_intent(value: str) -> tuple[str, str]:
    cleaned = strip_leading_articles(normalize_text(value))
    intent = "app"

    for hint in sorted(WEBSITE_HINT_WORDS, key=len, reverse=True):
        if has_target_hint(cleaned, hint):
            intent = "website"
            cleaned = remove_target_hint(cleaned, hint)

    for hint in sorted(APP_HINT_WORDS, key=len, reverse=True):
        if has_target_hint(cleaned, hint):
            cleaned = remove_target_hint(cleaned, hint)
            if intent != "website":
                intent = "app"

    return clean_target_name(cleaned), intent


def strip_leading_articles(value: str) -> str:
    cleaned = value.strip()
    for article in ("the ", "a ", "an "):
        if cleaned.startswith(article):
            return cleaned[len(article) :].strip()
    return cleaned


def has_target_hint(value: str, hint: str) -> bool:
    return (
        value == hint
        or value.startswith(f"{hint} ")
        or value.endswith(f" {hint}")
        or f" {hint} " in value
    )


def remove_target_hint(value: str, hint: str) -> str:
    cleaned = value.strip()
    cleaned = re.sub(rf"^{re.escape(hint)}\s+", "", cleaned)
    cleaned = re.sub(rf"\s+{re.escape(hint)}$", "", cleaned)
    cleaned = re.sub(rf"\s+{re.escape(hint)}\s+", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def looks_like_domain(value: str) -> bool:
    normalized = value.lower().strip()
    return "." in normalized and " " not in normalized


def resolve_website_target(value: str) -> str:
    normalized = normalize_text(value)
    return WEBSITE_ALIASES.get(normalized, value.strip())


def strip_filler(value: str) -> str:
    cleaned = normalize_text(value)
    changed = True
    while changed:
        changed = False
        for prefix in FILLER_PREFIXES:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()
                changed = True
                break
    return cleaned


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run your local JARVIS assistant.")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Listen through the microphone instead of typing commands.",
    )
    parser.add_argument(
        "--recognition",
        choices=("offline", "online", "auto"),
        default="offline",
        help="Speech recognition engine for voice mode. Offline uses PocketSphinx.",
    )
    args = parser.parse_args()
    Jarvis(voice=args.voice, recognition=args.recognition).run()
