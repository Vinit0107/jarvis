# Privacy

Local JARVIS is designed to keep laptop control local by default.

## What stays local

- App launching decisions
- Saved notes in `notes/`
- Windows Start Menu app cache in `start_apps_cache.json`
- Offline voice recognition when using `--recognition offline`

## What can use the internet

- `search ...` opens a browser search.
- `visit ...` or `open website ...` opens a website.
- `--recognition online` uses Google's speech recognizer through the `SpeechRecognition` package.

## Git hygiene

The repo ignores local notes, cache files, bytecode, virtual environments, and machine-specific VS Code settings.
