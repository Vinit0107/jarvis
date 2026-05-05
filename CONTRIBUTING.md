# Contributing

Thanks for helping improve Local JARVIS.

## Local checks

Run these before opening a pull request:

```powershell
python -m py_compile jarvis.py
python -m unittest discover -s tests -v
```

## Development notes

- Keep commands safe by default. Unknown app names should not unexpectedly open websites.
- Keep local files private. Do not commit `notes/`, `start_apps_cache.json`, or machine-specific VS Code settings.
- Prefer small changes with clear tests for command parsing, app routing, and startup behavior.
- If a change needs internet, document the offline fallback.

## Pull requests

Use the pull request template and include:

- what changed,
- how it was tested,
- any privacy, startup, or app-launching impact.
