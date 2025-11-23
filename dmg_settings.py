import os.path

# Volume name
volume_name = "Papyrus Installer"

# DMG format
format = "UDZO"

# Window settings
window_rect = ((200, 200), (410, 420))
background = None  # Use default white/finder background
default_view = "icon-view"
text_size = 12
icon_size = 80

# Icon positions
files = [
    "dist/Papyrus.app",
    "LICENSE",
    "README.md"
]

symlinks = {
    "Applications": "/Applications"
}

icon_locations = {
    "Papyrus.app": (100, 105),
    "Applications": (310, 105),
    "LICENSE": (100, 295),
    "README.md": (310, 295)
}

# License agreement
license = {
    "default-language": "en_US",
    "licenses": {
        "en_US": "LICENSE"
    }
}
