# FX Hotkeys

Windows app with a modern UI for **per-program keyboard shortcuts**, typed-text macros, and auto-save.

---

## Features

- Independent hotkeys per program (or global for all apps)
- Customizable steps: `key` · `type {TEXT}` · `wait` · `click`
- Per-program **Clear filters** key (`{CLEAR}` in steps)
- Colored themes (Dark / Light) with a modern look
- System tray support and optional start with Windows
- Export / import settings

---

## Easiest way to get Setup.exe (no Python needed)

1. Upload this folder to a new GitHub repository.
2. Open the **Actions** tab → **Build Windows installer** → **Run workflow**.
3. After a few minutes, download **Artifacts → FXHotkeys-Setup** (contains `FXHotkeys-Setup.exe`).

---

## Build on your PC

1. Install [Python 3.12](https://www.python.org/downloads/) (check **Add to PATH**) and [Inno Setup 6](https://jrsoftware.org/isdl.php).
2. Double-click `build.bat`.
3. Output: `installer_output\FXHotkeys-Setup.exe`  
   (portable build: `dist\FXHotkeys\FXHotkeys.exe`).

---

## Run from source

```bash
pip install -r requirements.txt
python main.py
```

---

## Notes

- Keep **NumLock** on if you use Numpad keys.
- If the target app runs as administrator, run FX Hotkeys as administrator too (from Settings).
- Settings path: `%AppData%\FXHotkeys\config.json`  
  Errors are logged to `error.log` next to it.
- Step format example:

```
key t
key b
type {TEXT}
key {CLEAR}
key down
key enter
```

- `{TEXT}` = the shortcut’s text field  
- `{CLEAR}` = clear-filters key (set per program; default `ctrl+tab`)

---

## License

Free for personal use. If you redistribute or modify it, please credit the original project.
