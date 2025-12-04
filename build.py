import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parent
APP_NAME = "Papyrus"
DMG_VOLUME = f"{APP_NAME} Installer"
DIST_DIR = PROJECT_ROOT / "dist"
APP_PATH = DIST_DIR / f"{APP_NAME}.app"
DMG_PATH = DIST_DIR / f"{APP_NAME}.dmg"
DMG_TEMP = DIST_DIR / f"{APP_NAME}_temp.dmg"
DMG_STAGING = DIST_DIR / f"{APP_NAME}_dmg"
LICENSE_FILE = PROJECT_ROOT / "LICENSE.txt"
README_FILE = PROJECT_ROOT / "README.md"
ICON_SOURCE = PROJECT_ROOT / "src" / "assets" / "papyrus.icns"

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
RED = "\033[0;31m"
NC = "\033[0m"


def log(message: str, color: str = NC) -> None:
    print(f"{color}{message}{NC}")


def run_command(command: Sequence[os.PathLike | str]) -> None:
    display = " ".join(map(str, command))
    print(f"Running: {display}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        print(f"Error running command: {display}")
        sys.exit(1)


def get_project_version(default: str = "0.0.0") -> str:
    pyproject = PROJECT_ROOT / "pyproject.toml"
    if not pyproject.exists():
        return default
    try:
        with pyproject.open("rb") as fp:
            data = tomllib.load(fp)
        return data["project"]["version"]
    except Exception:
        return default


APP_VERSION = get_project_version("1.2.0")


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


def create_qt_conf(app_path: Path):
    log("📝 Creating qt.conf for Qt plugin resolution...", YELLOW)
    resources_path = app_path / "Contents" / "Resources"
    resources_path.mkdir(parents=True, exist_ok=True)
    qt_conf_path = resources_path / "qt.conf"
    py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
    plugins_rel = f"../Resources/lib/{py_ver}/PySide6/Qt/plugins"
    qt_conf_path.write_text(f"[Paths]\nPlugins = {plugins_rel}\n")
    log(f"   Created {qt_conf_path} -> {plugins_rel}", GREEN)


def clean_frameworks(app_path: Path):
    """Manually removes unused frameworks to reduce app size."""
    log("🧹 Removing unused frameworks...", YELLOW)
    frameworks_path = app_path / "Contents" / "Frameworks"
    resources_qt_path = (
        app_path
        / "Contents"
        / "Resources"
        / "lib"
        / "python3.13"
        / "PySide6"
        / "Qt"
        / "lib"
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

    for base_path in (frameworks_path, resources_qt_path):
        if not base_path.exists():
            continue
        for fw in unused_frameworks:
            fw_path = base_path / fw
            if fw_path.exists():
                log(f"   Removing {fw}...", YELLOW)
                if fw_path.is_dir():
                    shutil.rmtree(fw_path)
                else:
                    fw_path.unlink()


def set_volume_icon(mount_point: Path) -> None:
    if not ICON_SOURCE.exists():
        log(f"⚠️ Icon file not found at {ICON_SOURCE}", YELLOW)
        return

    volume_icon_dest = mount_point / ".VolumeIcon.icns"
    shutil.copy(ICON_SOURCE, volume_icon_dest)
    setfile = shutil.which("SetFile")
    if setfile:
        run_command([setfile, "-a", "C", str(mount_point)])
        run_command([setfile, "-a", "V", str(volume_icon_dest)])
    else:
        log("⚠️ 'SetFile' not available; skipping volume icon attributes", YELLOW)


def configure_finder_window():
    applescript = f"""
    tell application "Finder"
        set d to disk "{DMG_VOLUME}"
        open d
        delay 1
        set w to container window of d
        set current view of w to icon view
        set toolbar visible of w to false
        set statusbar visible of w to false
        set icon size of icon view options of w to 100
        set arrangement of icon view options of w to not arranged
        set position of item "{APP_NAME}.app" of w to {{125, 130}}
        set position of item "Applications" of w to {{375, 130}}
        set bounds of w to {{200, 200, 700, 520}}
        update d
        delay 1
        close w
    end tell
    tell application "System Events"
        if process "Finder" exists then
            set visible of process "Finder" to false
        end if
    end tell
    """
    subprocess.run(["osascript", "-e", applescript], check=True)


def stage_dmg_contents(app_path: Path) -> Path:
    if DMG_STAGING.exists():
        shutil.rmtree(DMG_STAGING)
    DMG_STAGING.mkdir(parents=True, exist_ok=True)

    shutil.copytree(app_path, DMG_STAGING / f"{APP_NAME}.app")

    applications_link = DMG_STAGING / "Applications"
    if applications_link.exists() or applications_link.is_symlink():
        applications_link.unlink()
    os.symlink("/Applications", applications_link)

    ds_store = DMG_STAGING / ".DS_Store"
    if ds_store.exists():
        ds_store.unlink()

    return DMG_STAGING


def build_dmg(app_path: Path):
    log("💿 Creating DMG...", BLUE)
    if DMG_PATH.exists():
        DMG_PATH.unlink()
    if DMG_TEMP.exists():
        DMG_TEMP.unlink()

    stage_dmg_contents(app_path)

    run_command(
        [
            "hdiutil",
            "create",
            "-volname",
            DMG_VOLUME,
            "-srcfolder",
            str(DMG_STAGING),
            "-ov",
            "-format",
            "UDRW",
            str(DMG_TEMP),
        ]
    )

    log("   Mounting DMG for styling...", YELLOW)
    attach_output = subprocess.check_output(
        ["hdiutil", "attach", str(DMG_TEMP), "-readwrite", "-noverify", "-noautoopen"],
        text=True,
    )

    device = None
    mount_point = None
    for line in attach_output.splitlines():
        if not line.startswith("/dev/"):
            continue

        parts = line.split()
        if device is None:
            device = parts[0]

        if "/Volumes/" in line:
            mount_path = line[line.index("/Volumes/") :].strip()
            mount_point = Path(mount_path)
            device = parts[0]
            break

    if not device or not mount_point:
        log("❌ Failed to mount DMG", RED)
        sys.exit(1)

    try:
        set_volume_icon(mount_point)
        configure_finder_window()
    finally:
        run_command(["hdiutil", "detach", device, "-force"])

    run_command(
        ["hdiutil", "convert", str(DMG_TEMP), "-format", "UDZO", "-o", str(DMG_PATH)]
    )
    if DMG_TEMP.exists():
        DMG_TEMP.unlink()
    if DMG_STAGING.exists():
        shutil.rmtree(DMG_STAGING)

    log(f"✔ DMG ready at {DMG_PATH}", GREEN)


def build():
    log("🧹 Cleaning previous artifacts...", YELLOW)
    eject_dmg(DMG_VOLUME)

    for path in (PROJECT_ROOT / "build", APP_PATH, DMG_PATH, DMG_TEMP, DMG_STAGING):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    DIST_DIR.mkdir(exist_ok=True)

    log("📦 Building application with py2app...", BLUE)
    try:
        run_command([sys.executable, "setup.py", "py2app"])
    except SystemExit:
        if not APP_PATH.exists():
            raise
        log("⚠️ py2app exited with error, but app bundle exists. Continuing...", YELLOW)

    if not APP_PATH.exists():
        log("❌ Application bundle not found after build", RED)
        sys.exit(1)

    create_qt_conf(APP_PATH)
    clean_frameworks(APP_PATH)

    if shutil.which("codesign"):
        log("✍️ Signing the .app bundle (ad-hoc)...", BLUE)
        run_command(["codesign", "--force", "--deep", "--sign", "-", str(APP_PATH)])
        run_command(
            ["codesign", "--verify", "--deep", "--strict", "--verbose=2", str(APP_PATH)]
        )
    else:
        log("⏭️ Skipping signing: 'codesign' not available", YELLOW)

    log("🔧 Patching binaries for Qt version alignment...", BLUE)
    qt_core_path = (
        APP_PATH
        / "Contents"
        / "Resources"
        / "lib"
        / "python3.13"
        / "PySide6"
        / "QtCore.abi3.so"
    )
    executable_path = APP_PATH / "Contents" / "MacOS" / APP_NAME

    if qt_core_path.exists():
        run_command(
            [
                "install_name_tool",
                "-change",
                "@rpath/libpyside6.abi3.6.9.dylib",
                "@rpath/libpyside6.abi3.6.10.dylib",
                str(qt_core_path),
            ]
        )
        run_command(
            [
                "install_name_tool",
                "-change",
                "@rpath/libshiboken6.abi3.6.9.dylib",
                "@rpath/libshiboken6.abi3.6.10.dylib",
                str(qt_core_path),
            ]
        )
        try:
            run_command(
                [
                    "install_name_tool",
                    "-delete_rpath",
                    "/opt/homebrew/lib",
                    str(qt_core_path),
                ]
            )
        except SystemExit:
            log("   (RPATH /opt/homebrew/lib not found or already removed)", YELLOW)

        if shutil.which("codesign"):
            run_command(["codesign", "--force", "--sign", "-", str(qt_core_path)])

    if executable_path.exists():
        try:
            run_command(
                [
                    "install_name_tool",
                    "-add_rpath",
                    "@executable_path/../Frameworks",
                    str(executable_path),
                ]
            )
            if shutil.which("codesign"):
                run_command(
                    ["codesign", "--force", "--sign", "-", str(executable_path)]
                )
        except SystemExit:
            log(
                "   (RPATH might already exist or failed to add, proceeding...)", YELLOW
            )

    build_dmg(APP_PATH)

    if APP_PATH.exists():
        log(f"🧹 Removing intermediate {APP_PATH}...", YELLOW)
        shutil.rmtree(APP_PATH)

    log(
        f"✅ Build complete! Open {DMG_PATH} and drag {APP_NAME}.app into /Applications when ready.",
        GREEN,
    )


if __name__ == "__main__":
    log(f"🚀 Building {APP_NAME} v{APP_VERSION}", BLUE)
    build()
