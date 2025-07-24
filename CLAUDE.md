# Tickertock Project Context

## Overview
Tickertock is a Python application that integrates StreamDeck hardware with Clockify time tracking. It provides a visual interface on StreamDeck buttons to start/stop time tracking for different projects.

## Current Status (2025-07-24)
The application is **fully compatible** with the latest streamdeck-linux-gui. No changes were needed.

## Key Technical Details

### Dependencies
- **streamdeck-ui**: v2.0.15 (installed as streamdeck-ui, imports as streamdeck_ui)
- **PySide6**: Already migrated from PySide2
- **Python**: 3.11 (in virtual env at .env/)
- **Other deps**: pycairo, jinja2, filetype, toml, clockify, click, xdg

### Project Structure
```
tickertock/
├── pyproject.toml          # PEP 621 config (no setup.py)
├── tickertock/
│   ├── __init__.py
│   ├── clockify.py         # Clockify API integration
│   ├── config.py           # Configuration management
│   ├── tickertock.py       # Main application logic
│   ├── ui.py               # StreamDeck UI integration
│   ├── utils.py            # Utility functions
│   ├── scripts/
│   │   └── tickertock.py   # CLI entry point
│   └── skel/               # Template files
│       ├── assets/         # Icons and images
│       ├── config.toml.j2  # Config template
│       └── streamdeck_ui.json.j2
```

### Configuration Location
- User config: `~/.config/tickertock/`
- Contains: config.toml, projects.toml, streamdeck_ui.json.j2, assets/

### Known Issues & Workarounds

1. **image_filter.py TypeError**: Already handled by monkey-patch in ui.py:31-38
   ```python
   def _filetype_guess(*args, **kwargs):
       try:
           return filetype_guess(*args, **kwargs)
       except TypeError:
           return True
   ```

2. **streamdeck-linux-gui status**: Project is in maintenance mode only. They recommend StreamController for new features, but tickertock works fine with current version.

### CLI Commands
- `tickertock init --clockify-api-key KEY --clockify-workspace-id ID` - Initialize
- `tickertock ui` - Launch the UI (wrapper around streamdeck_ui)
- `tickertock toggle PROJECT` - Start/stop time tracking
- `tickertock writeout` - Export StreamDeck configuration
- `tickertock version` - Show version

### Testing Commands
When making changes, run these to verify:
```bash
# Check if package installs correctly
pip install -e .

# Test basic functionality
tickertock version

# Test device detection (if StreamDeck connected)
tickertock writeout

# Full UI test (requires display)
tickertock ui
```

### Important Notes
1. The application modifies streamdeck_ui behavior at runtime through monkey-patching
2. It detects StreamDeck device with ID: AL42K2C59265 (on this system)
3. Uses Jinja2 templates to generate StreamDeck configurations
4. Integrates with system tray for quick access

## Development Tips
- Always use the virtual environment at `.env/`
- The project uses PEP 621 (pyproject.toml) - no setup.py
- When debugging UI issues, check both tickertock and streamdeck_ui logs
- The bottom-right button on StreamDeck is special (shows status/cycles pages)

## Last Verified
- Date: 2025-07-24
- streamdeck-ui version: 2.0.15
- Python version: 3.11
- Platform: Linux 6.11.0-29-generic
- All functionality working correctly