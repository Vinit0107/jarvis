# Local JARVIS for Your Laptop

This is a lightweight local assistant inspired by JARVIS.

## What it does

- Opens real apps installed on your laptop, like Netflix, Prime Video, Chrome, Edge, File Explorer, Notepad, Calculator, Spotify, and VS Code
- Prefers installed Windows Start Menu apps and does not silently turn missing app launches into Chrome searches
- Understands natural app commands like `launch Google Chrome`, `start VS Code`, and `open calculator`
- Opens websites
- Searches the web
- Speaks responses if `pyttsx3` is installed
- Listens to microphone commands in voice mode
- Saves and reads notes
- Reports time, date, and basic system info

## Run it in text mode

```powershell
python jarvis.py
```

## Run the GUI

```powershell
python jarvis_gui.py
```

The GUI includes:

- a conversation log,
- typed command input,
- quick action buttons,
- app shortcut visibility,
- a `Listen Once` button with `offline`, `online`, and `auto` recognition modes.

In the GUI, `Listen Once` accepts both wake-word commands and direct commands. You can say `Jarvis open Chrome` or just `open Chrome`.

## Run it in voice mode

```powershell
pip install -r requirements.txt
python jarvis.py --voice
```

Offline voice mode is the default:

```powershell
python jarvis.py --voice --recognition offline
```

Online voice mode is still available if you want Google's recognizer:

```powershell
python jarvis.py --voice --recognition online
```

In voice mode, say `Jarvis` before the command:

- `Jarvis open chrome`
- `Jarvis open Netflix`
- `Jarvis open Prime Video`
- `Jarvis open File Explorer`
- `Jarvis open calculator`
- `Jarvis visit youtube.com`
- `Jarvis apps`
- `Jarvis what time is it`
- `Jarvis search Iron Man suit`
- `Jarvis note call mom tomorrow`
- `exit`

Voice mode uses your microphone plus the `SpeechRecognition` package. Offline mode uses `pocketsphinx`, so command recognition works without the internet. Web searches and websites still need internet because those actions open the browser.

## Start automatically after restart

Run this once from PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install_startup.ps1
```

That creates a Windows Task Scheduler task named `Local JARVIS Offline Voice`. If Task Scheduler is blocked by permissions, it automatically creates a Startup folder launcher instead. After you shut down or restart the PC, JARVIS starts again when you log into Windows.

To remove the startup automation:

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall_startup.ps1
```

For better accuracy, speak the wake word first, pause briefly, then give a short command:

- `Jarvis, open Google Chrome`
- `Jarvis, launch VS Code`
- `Jarvis, visit youtube.com`
- `Jarvis, search for Python tutorials`
- `Jarvis, what time is it`

## Run it from VS Code

Use the Run and Debug panel and choose one of these configurations:

- `JARVIS: Run text mode`
- `JARVIS: Run voice mode`
- `JARVIS: Run GUI`

You can also press `Ctrl+Shift+P`, choose `Tasks: Run Task`, and run:

- `JARVIS: Install voice requirements`
- `JARVIS: Run text mode`
- `JARVIS: Run voice mode`
- `JARVIS: Run GUI`

## Testing

Run the same checks used by GitHub Actions:

```powershell
python -m py_compile jarvis.py
python -m py_compile jarvis_gui.py
python -m unittest discover -s tests -v
```

## Repository health

This repo includes:

- GitHub Actions CI for compile and unit test checks
- Dependabot for Python and GitHub Actions updates
- Issue templates and a pull request template
- Privacy, security, support, and contribution docs
- A `.gitignore` that keeps notes, app cache data, bytecode, and local settings private

## Example commands

- `help`
- `apps`
- `open chrome`
- `open Netflix`
- `open Prime Video`
- `open WhatsApp`
- `open edge`
- `open file explorer`
- `visit youtube.com`
- `open website netflix.com`
- `launch Google Chrome`
- `start VS Code`
- `open calculator`
- `open notepad`
- `open vscode`
- `open youtube.com`
- `search arc reactor`
- `time`
- `date`
- `system info`
- `note buy groceries`
- `list notes`
- `read note`
- `exit`

## Customize app shortcuts

JARVIS opens laptop apps in two ways. First, it reads installed Windows Start Menu apps, so Store apps and PWAs like Netflix, Prime Video, and WhatsApp can launch as apps. Second, it uses shortcuts in [jarvis_apps.json](jarvis_apps.json) for classic `.exe` apps.

Current app shortcuts:

- `chrome`
- `edge`
- `file explorer`
- `notepad`
- `calculator`
- `paint`
- `settings`
- `vscode`
- `task manager`
- `terminal`
- `spotify`
