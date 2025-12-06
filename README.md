# Papyrus

```text
██████╗  █████╗ ██████╗ ██╗   ██╗██████╗ ██╗   ██╗███████╗
██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██║   ██║██╔════╝
██████╔╝███████║██████╔╝ ╚████╔╝ ██████╔╝██║   ██║███████╗
██╔═══╝ ██╔══██║██╔═══╝   ╚██╔╝  ██╔══██╗██║   ██║╚════██║
██║     ██║  ██║██║        ██║   ██║  ██║╚██████╔╝███████║
╚═╝     ╚═╝  ╚═╝╚═╝        ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

## Papyrus — HTML to PDF Converter for macOS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### ⚡ About

Papyrus is a beautiful, modern HTML to PDF converter and previewer for macOS. Paste HTML code, see it rendered instantly, and print to PDF with custom styling. Perfect for developers, designers, and anyone who works with HTML.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### ✨ Highlights

- 👁️ **Instant Preview** – See your HTML rendered in real-time as you type
- 🎨 **Syntax Highlighting** – Color-coded HTML editor for easy reading
- 🌙 **Beautiful Defaults** – Automatically wraps unstyled HTML in a modern dark theme
- 🖨️ **Print Ready** – Custom headers and footers for professional printed pages
- 📋 **PDF Copy** – Copy code snippets directly from the generated PDF
- ✂️ **Smart Paste** – Cleans and formats pasted HTML automatically
- 📄 **Multiple Pages** – Handles long documents with proper pagination
- 🖥️ **Apple Silicon Native** – Optimized for M1/M2/M3/M4 chips

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 📦 Installation

1. Download the latest `Papyrus.dmg` from [Releases](https://github.com/RazorBackRoar/Papyrus/releases)
2. Mount the DMG → drag `Papyrus.app` into `/Applications` → eject
3. First launch (Gatekeeper):

   - **Method A:** Right-click `Papyrus.app` → _Open_ → confirm
   - **Method B:**

     ```bash
     sudo xattr -cr /Applications/Papyrus.app
     ```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 🚀 Usage

1. **Paste HTML:** Paste or type HTML code in the left editor pane
2. **Preview:** Watch the right pane update with your rendered HTML
3. **Print to PDF:** Press `Cmd+P` or click Print to generate PDF
4. **Customize:** Add headers/footers using the options panel

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 🎨 Auto-Styling

When you paste HTML without CSS, Papyrus automatically applies a beautiful dark theme:

```html
<!-- Your input -->
<h1>Hello World</h1>
<p>Some text here</p>

<!-- Papyrus wraps it with -->
<html>
<head>
  <style>
    body { background: #1a1a2e; color: #eee; font-family: system-ui; }
    /* ... modern dark theme styles ... */
  </style>
</head>
<body>
  <h1>Hello World</h1>
  <p>Some text here</p>
</body>
</html>
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 💻 Requirements

- macOS 10.13 (High Sierra) or later
- ~2 GB free disk space
- No Python install needed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 🔧 Troubleshooting

- **"App is damaged / Cannot be opened"** – Use the Gatekeeper override above
- **Preview not updating** – Check for HTML syntax errors
- **PDF not generating** – Ensure the HTML is valid and renderable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 🛠️ Building from Source

```bash
# Clone repository
git clone https://github.com/RazorBackRoar/Papyrus.git
cd Papyrus

# Install dependencies
pip install -r requirements.txt

# Run from source
python src/papyrus/main.py

# Build standalone app
python build/scripts/build.py
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 📜 License

MIT License – see `LICENSE.txt`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 🐞 Support

- Issues: <https://github.com/RazorBackRoar/Papyrus/issues>
- Source: <https://github.com/RazorBackRoar/Papyrus>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 🔐 Privacy

Papyrus runs 100% locally. No telemetry, no analytics, no cloud features. Your HTML stays on your machine.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 👤 Author

**RazorBackRoar**

GitHub: [@RazorBackRoar](https://github.com/RazorBackRoar)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
