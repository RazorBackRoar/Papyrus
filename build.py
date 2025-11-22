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
    
    dmg_name = "Papyrus-v1.0.0-macOS.dmg"
    dmg_path = os.path.join("dist", dmg_name)

    # Remove existing DMG if it exists
    if os.path.exists(dmg_path):
        print(f"   Removing existing DMG: {dmg_path}")
        os.remove(dmg_path)

    try:
        import dmgbuild
        print("   Using dmgbuild to create customized DMG...")
        
        # Define settings programmatically to avoid path issues
        settings = {
            'volume_name': 'Papyrus Installer',
            'format': 'UDZO',
            'window_rect': ((200, 200), (410, 420)),
            'icon_size': 80,
            'files': [app_path, 'LICENSE', 'README.md'],
            'symlinks': {'Applications': '/Applications'},
            'icon_locations': {
                'Papyrus.app': (100, 105),
                'Applications': (310, 105),
                'LICENSE': (100, 295),
                'README.md': (310, 295)
            }
        }
        
        dmgbuild.build_dmg(dmg_path, 'Papyrus Installer', settings=settings)
        print(f"🎉 Build Complete! DMG at {dmg_path}")
        
    except ImportError:
        print("⚠️ 'dmgbuild' not found. Falling back to simple hdiutil...")
        print("   (Install dmgbuild with: pip install dmgbuild for customized layout)")
        
        # Fallback to simple DMG
        staging_dir = "dist/dmg_source"
        if os.path.exists(staging_dir):
            shutil.rmtree(staging_dir)
        os.makedirs(staging_dir, exist_ok=True)
        
        shutil.copytree(app_path, os.path.join(staging_dir, "Papyrus.app"))
        shutil.copy("LICENSE", staging_dir)
        shutil.copy("README.md", staging_dir)
        os.symlink("/Applications", os.path.join(staging_dir, "Applications"))
        
        run_command(f"hdiutil create -volname 'Papyrus Installer' -srcfolder '{staging_dir}' -ov -format UDZO '{dmg_path}'")
        
        # Cleanup
        shutil.rmtree(staging_dir)
        print(f"✅ Build Complete! (Standard layout) DMG at {dmg_path}")

if __name__ == "__main__":
    build()
