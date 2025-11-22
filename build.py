import os
import shutil
import subprocess
import sys

def run_command(command):
    print(f"Running: {command}")
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        sys.exit(1)

def eject_dmg(volname):
    """Ejects the DMG volume if it is mounted."""
    try:
        result = subprocess.run(
            ['hdiutil', 'info'],
            capture_output=True,
            text=True,
            check=True
        )
        if volname in result.stdout:
            print(f"   Ejecting existing '{volname}' volume...")
            subprocess.run(['hdiutil', 'detach', f"/Volumes/{volname}"],
                         capture_output=True, check=False)
    except subprocess.CalledProcessError:
        pass

def build():
    print("🧹 Cleaning up previous builds...")
    eject_dmg("Papyrus Installer")

    # Clean dist and build directories
    for directory in ["dist", "build"]:
        if os.path.exists(directory):
            print(f"   Removing {directory}/")
            shutil.rmtree(directory)

    # Build the .app with py2app
    print("📦 Building the .app bundle with py2app...")
    try:
        run_command(f"{sys.executable} setup.py py2app")
    except SystemExit:
        # Check if app was created despite error
        if not os.path.exists("dist/Papyrus.app"):
            raise
        print("⚠️ py2app exited with error, but app bundle was created. Proceeding...")

    # Sign the app (ad-hoc)
    print("✍️ Signing the .app bundle (ad-hoc)...")
    app_path = "dist/Papyrus.app"
    run_command(f"codesign --force --deep --sign - '{app_path}'")

    # Verify signature
    print("✅ Verifying the ad-hoc signature...")
    run_command(f"codesign --verify --deep --strict --verbose=2 '{app_path}'")

    # Create DMG
    print("💿 Creating the distributable DMG...")
    if shutil.which("create-dmg"):
        dmg_name = "Papyrus-v1.0.0-macOS.dmg"
        dmg_path = os.path.join("dist", dmg_name)

        # Remove existing DMG if it exists
        if os.path.exists(dmg_path):
            print(f"   Removing existing DMG: {dmg_path}")
            os.remove(dmg_path)

        # Clean staging directory first to avoid size bloat
        staging_dir = "dist/dmg_source"
        if os.path.exists(staging_dir):
            print("   Cleaning old staging directory...")
            try:
                shutil.rmtree(staging_dir)
            except OSError:
                run_command(f"rm -rf {staging_dir}")

        # Create fresh staging directory for DMG content
        os.makedirs(staging_dir, exist_ok=True)

        # Copy App, LICENSE, and README to staging
        print("   Copying files to DMG staging area...")
        shutil.copytree(app_path, os.path.join(staging_dir, "Papyrus.app"))
        shutil.copy("LICENSE", staging_dir)
        shutil.copy("README.md", staging_dir)

        # Create symbolic link to /Applications for drag-and-drop installation
        print("   Creating Applications symlink...")
        applications_link = os.path.join(staging_dir, "Applications")
        if not os.path.exists(applications_link):
            os.symlink("/Applications", applications_link)

        # Create DMG from staging directory
        # Window size: 410x420
        # Window position: 200,200 (avoid left edge where dock is)
        run_command(f"create-dmg \
            --volname 'Papyrus Installer' \
            --window-pos 200 200 \
            --window-size 410 420 \
            --icon-size 80 \
            --text-size 11 \
            --icon 'Papyrus.app' 100 105 \
            --icon 'Applications' 310 105 \
            --icon 'LICENSE' 100 295 \
            --icon 'README.md' 310 295 \
            --hide-extension 'Papyrus.app' \
            --no-internet-enable \
            '{dmg_path}' \
            '{staging_dir}'")

        # Cleanup staging directory after successful build to save space
        print("   Cleaning up staging directory...")
        if os.path.exists(staging_dir):
            shutil.rmtree(staging_dir)

        print(f"🎉 Build Complete! DMG at {dmg_path}")
    else:
        print("⚠️ 'create-dmg' not found. Skipping DMG creation.")
        print("Install it with: brew install create-dmg")

if __name__ == "__main__":
    build()
