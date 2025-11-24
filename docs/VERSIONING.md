# Automated Versioning Workflow

This workflow describes how to maintain a single source of truth for your application's version number and automatically propagate it to all relevant files during the build process.

## 1. Identify Version Locations

First, identify all files where the version number is hardcoded. Common locations include:

- `src/main.py` (or your entry point)
- `setup.py` (for packaging)
- `package.json` (for Node.js apps)
- `Info.plist` (for macOS apps)

## 2. Create/Update Build Script

In your `build.sh` (or `build_script.sh`), define a `VERSION` variable at the top. This will be your single source of truth.

```bash
#!/bin/bash

# --- Version Configuration ---
VERSION="1.0.0"
echo "Setting version to $VERSION..."
```

## 3. Add Update Commands

Use `sed` (Stream Editor) to find and replace the version strings in your target files.

**Note for macOS users**: macOS `sed` requires an empty extension `''` after `-i` for in-place edits. Linux users should remove the `''`.

### Example for Python (main.py)

If your `main.py` has:

```python
"""
Version: 0.0.0
"""
...
app.setApplicationVersion("0.0.0")
```

Add this to `build.sh`:

```bash
# Update docstring version
sed -i '' "s/Version: [0-9]*\.[0-9]*\.[0-9]*/Version: $VERSION/" src/main.py

# Update setApplicationVersion
sed -i '' "s/app.setApplicationVersion(\"[0-9]*\.[0-9]*\.[0-9]*\")/app.setApplicationVersion(\"$VERSION\")/" src/main.py
```

### Example for setup.py

If your `setup.py` has:

```python
OPTIONS = {
    "CFBundleVersion": "0.0.0",
    "CFBundleShortVersionString": "0.0.0",
}
```

Add this to `build.sh`:

```bash
sed -i '' "s/\"CFBundleVersion\": \"[0-9]*\.[0-9]*\.[0-9]*\"/\"CFBundleVersion\": \"$VERSION\"/" setup.py
sed -i '' "s/\"CFBundleShortVersionString\": \"[0-9]*\.[0-9]*\.[0-9]*\"/\"CFBundleShortVersionString\": \"$VERSION\"/" setup.py
```

## 4. Run the Build

Execute your build script. It will now update all files to match the `VERSION` variable before building.

```bash
./build.sh
```

## 5. Verify

Check your source files to ensure the version numbers have been updated to match the one in `build.sh`.
