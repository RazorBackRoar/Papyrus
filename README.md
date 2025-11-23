# Papyrus

Papyrus is a beautiful, modern HTML to PDF converter and previewer for macOS. It allows you to paste HTML code, preview it instantly, and print it to PDF with custom styling.

## Features

- **Instant Preview**: See your HTML rendered as you type.
- **Syntax Highlighting**: Color-coded HTML editor.
- **Beautiful Defaults**: Automatically adds a modern dark theme wrapper if your HTML lacks styles.
- **Print Ready**: Add custom headers and footers (bands) to your printed pages.
- **PDF Copy**: Copy code snippets directly from the generated PDF.

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/RazorBackRoar/Papyrus.git
   cd Papyrus
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. Run the application:
   ```bash
   python3 main.py
   ```

## Building

To build a standalone macOS application (.app) and disk image (.dmg):

1. Ensure you have `create-dmg` installed:
   ```bash
   brew install create-dmg
   ```

2. Run the build script:
   ```bash
   python3 build.py
   ```

The artifacts will be in the `dist/` directory.

## License

MIT License
