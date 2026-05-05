# Support

Use GitHub issues for bugs and feature requests.

Before opening an issue, please check:

- You are running a supported Python version.
- Voice dependencies are installed with `pip install -r requirements.txt`.
- Your microphone is allowed in Windows privacy settings.
- You ran `refresh apps` after installing new apps.

Useful diagnostics:

```powershell
python --version
python jarvis.py --help
python -m unittest discover -s tests -v
```
