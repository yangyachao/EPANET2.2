# EPANET PySide6 GUI

Modern cross-platform GUI for EPANET 2.2 built with PySide6 (Qt for Python).

## Features

- Cross-platform (Windows, Linux, macOS)
- Modern Qt-based interface
- Interactive network map editor
- Real-time simulation visualization
- Comprehensive data management

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Requirements

- Python 3.8+
- PySide6
- EPANET 2.2 library (epanet2.dll / libepanet2.so / libepanet2.dylib)

## Project Structure

```
epanet_pyside6/
├── core/           # Core engine integration
├── models/         # Data models
├── gui/            # GUI components
├── io/             # File I/O
├── graphics/       # Rendering
├── analysis/       # Analysis tools
└── utils/          # Utilities
```

## License

MIT License - Same as EPANET 2.2
