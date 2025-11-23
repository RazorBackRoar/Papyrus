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
            ["hdiutil", "info"], capture_output=True, text=True, check=True
        )
        if volname in result.stdout:
            print(f"   Ejecting existing '{volname}' volume...")
            subprocess.run(
                ["hdiutil", "detach", f"/Volumes/{volname}"],
                capture_output=True,
                check=False,
            )
    except subprocess.CalledProcessError:
        pass


def create_qt_conf(app_path):
    print("📝 Creating qt.conf for Qt plugin resolution...")
    resources_path = os.path.join(app_path, "Contents", "Resources")
    qt_conf_path = os.path.join(resources_path, "qt.conf")
    py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
    plugins_rel = f"../Resources/lib/{py_ver}/PySide6/Qt/plugins"
    qt_conf_content = f"[Paths]\nPlugins = {plugins_rel}\n"
    with open(qt_conf_path, "w") as f:
        f.write(qt_conf_content)
    print(f"   Created {qt_conf_path} -> {plugins_rel}")


def clean_frameworks(app_path):
    """Manually removes unused frameworks to reduce app size."""
    print("🧹 Manually removing unused frameworks...")
    frameworks_path = os.path.join(app_path, "Contents", "Frameworks")
    resources_qt_path = os.path.join(
        app_path, "Contents", "Resources", "lib", "python3.13", "PySide6", "Qt", "lib"
    )

    unused_frameworks = [
        "QtWebEngineCore.framework",
        "QtWebEngineWidgets.framework",
        "QtWebEngineQuick.framework",
        "QtDesigner.framework",
        "QtQuick3D.framework",
        "QtQuick3DRuntimeRender.framework",
        "QtQuick3DUtils.framework",
        "QtDataVisualization.framework",
        "QtCharts.framework",
        "QtLocation.framework",
        "QtMultimedia.framework",
        "QtMultimediaWidgets.framework",
        "QtSensors.framework",
        "QtSerialPort.framework",
        "QtSql.framework",
        "QtTest.framework",
        "QtTextToSpeech.framework",
        "QtXml.framework",
        "QtBluetooth.framework",
        "QtNfc.framework",
        "QtPositioning.framework",
        "QtPositioningQuick.framework",
        "QtRemoteObjects.framework",
        "QtScxml.framework",
        "QtStateMachine.framework",
        "QtWebChannel.framework",
        "QtWebChannelQuick.framework",
        "QtWebSockets.framework",
        "QtPdf.framework",
        "QtPdfWidgets.framework",
        "QtVirtualKeyboard.framework",
        "Qt3DCore.framework",
        "Qt3DRender.framework",
        "Qt3DInput.framework",
        "Qt3DLogic.framework",
        "Qt3DExtras.framework",
        "Qt3DAnimation.framework",
    ]

    for base_path in [frameworks_path, resources_qt_path]:
        if not os.path.exists(base_path):
            continue
        for fw in unused_frameworks:
            fw_path = os.path.join(base_path, fw)
            if os.path.exists(fw_path):
                print(f"   Removing {fw}...")
                if os.path.isdir(fw_path):
                    shutil.rmtree(fw_path)
                else:
                    os.remove(fw_path)


def build():
    print("🧹 Cleaning up previous builds...")
    eject_dmg("Papyrus Installer")

    # Clean dist and build directories
    for directory in ["dist", "build"]:
        if os.path.exists(directory):
            print(f"   Removing {directory}/")
            shutil.rmtree(directory)

    # Run py2app
    print("📦 Building application with py2app...")
    try:
        run_command(f"{sys.executable} setup.py py2app")
    except SystemExit:
        # Check if app was created despite error
        if not os.path.exists("dist/Papyrus.app"):
            raise
        print("⚠️ py2app exited with error, but app bundle was created. Proceeding...")

    app_path = "dist/Papyrus.app"
    create_qt_conf(app_path)
    clean_frameworks(app_path)

    app_path = "dist/Papyrus.app"
    if shutil.which("codesign"):
        print("✍️ Signing the .app bundle (ad-hoc)...")
        run_command(f"codesign --force --deep --sign - '{app_path}'")
        print("✅ Verifying the ad-hoc signature...")
        run_command(f"codesign --verify --deep --strict --verbose=2 '{app_path}'")
    else:
        print("⏭️ Skipping signing: 'codesign' not available")

    # --- Patching for Qt Version Mismatch & RPATH ---
    print("🔧 Patching binaries for Qt version mismatch and RPATH...")
    qt_core_path = os.path.join(
        app_path,
        "Contents",
        "Resources",
        "lib",
        "python3.13",
        "PySide6",
        "QtCore.abi3.so",
    )
    executable_path = os.path.join(app_path, "Contents", "MacOS", "Papyrus")

    # 1. Patch QtCore.abi3.so to point to 6.10 instead of 6.9
    if os.path.exists(qt_core_path):
        run_command(
            f"install_name_tool -change @rpath/libpyside6.abi3.6.9.dylib @rpath/libpyside6.abi3.6.10.dylib '{qt_core_path}'"
        )
        run_command(
            f"install_name_tool -change @rpath/libshiboken6.abi3.6.9.dylib @rpath/libshiboken6.abi3.6.10.dylib '{qt_core_path}'"
        )
        # Remove system RPATH to prevent loading system Qt
        try:
            run_command(
                f"install_name_tool -delete_rpath /opt/homebrew/lib '{qt_core_path}'"
            )
        except SystemExit:
            print("   (RPATH /opt/homebrew/lib not found or already removed)")

        # Re-sign after patching
        if shutil.which("codesign"):
            run_command(f"codesign --force --sign - '{qt_core_path}'")

    # 2. Add RPATH to executable
    if os.path.exists(executable_path):
        # Check if RPATH already exists to avoid error
        try:
            run_command(
                f"install_name_tool -add_rpath @executable_path/../Frameworks '{executable_path}'"
            )
            # Re-sign after patching
            if shutil.which("codesign"):
                run_command(f"codesign --force --sign - '{executable_path}'")
        except SystemExit:
            print("   (RPATH might already exist or failed to add, proceeding...)")

    # ------------------------------------------------

    # Create DMG
    print("💿 Creating the distributable DMG...")

    dmg_name = "Papyrus.dmg"
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
            "volume_name": "Papyrus Installer",
            "format": "UDZO",
            "window_rect": ((200, 200), (540, 550)),
            "icon_size": 100,
            "files": [app_path, "LICENSE.txt", "README.md"],
            "symlinks": {"Applications": "/Applications"},
            "icon_locations": {
                "Papyrus.app": (140, 120),
                "Applications": (400, 120),
                "LICENSE.txt": (140, 340),
                "README.md": (400, 340),
            },
        }

        dmgbuild.build_dmg(dmg_path, "Papyrus Installer", settings=settings)

        # Cleanup .app bundle to save space/confusion
        # if os.path.exists(app_path):
        #     print(f"🧹 Removing intermediate {app_path}...")
        #     shutil.rmtree(app_path)

        print(f"🎉 Build Complete! DMG at {dmg_path}")
        print(
            "👉 NOTE: Please open the DMG manually and drag Papyrus.app into /Applications"
        )

    except ImportError:
        print("⚠️ 'dmgbuild' not found. Falling back to simple hdiutil...")
        print("   (Install dmgbuild with: pip install dmgbuild for customized layout)")

        # Fallback to simple DMG
        staging_dir = "dist/dmg_source"
        if os.path.exists(staging_dir):
            shutil.rmtree(staging_dir)
        os.makedirs(staging_dir, exist_ok=True)

        shutil.copytree(app_path, os.path.join(staging_dir, "Papyrus.app"))
        shutil.copy("LICENSE.txt", staging_dir)
        shutil.copy("README.md", staging_dir)
        os.symlink("/Applications", os.path.join(staging_dir, "Applications"))

        run_command(
            f"hdiutil create -volname 'Papyrus Installer' -srcfolder '{staging_dir}' -ov -format UDZO '{dmg_path}'"
        )

        # Cleanup
        shutil.rmtree(staging_dir)
        # Cleanup .app bundle to save space/confusion
        # if os.path.exists(app_path):
        #     print(f"🧹 Removing intermediate {app_path}...")
        #     shutil.rmtree(app_path)

        print(f"✅ Build Complete! (Standard layout) DMG at {dmg_path}")
        print(
            "👉 NOTE: Please open the DMG manually and drag Papyrus.app into /Applications"
        )


if __name__ == "__main__":
    build()
