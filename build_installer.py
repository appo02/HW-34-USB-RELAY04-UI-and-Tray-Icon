"""
Build standalone .exe files for the USB-RELAY04 tool suite.

Usage:
    python build_installer.py

Produces:
    dist/USB-RELAY04/
        usb_relay_hw34_gui.exe
        relay_tray.exe
        usb_relay_hw34_cli.exe
        relay_mapping.cfg
        README.txt

Then run Inno Setup on installer.iss to create the final installer.
"""

import os
import sys
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(SCRIPT_DIR, "dist", "USB-RELAY04")


def run(cmd):
    print(f"\n{'='*60}")
    print(f"  {cmd}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=SCRIPT_DIR,
                            env={**os.environ, "PYTHONPATH": ""})
    if result.returncode != 0:
        print(f"FAILED (exit {result.returncode}): {cmd}")
        sys.exit(1)


# Use the same Python that is running this script
PYTHON = sys.executable


def main():
    # Clean previous build
    for folder in ["build", "dist"]:
        path = os.path.join(SCRIPT_DIR, folder)
        if os.path.exists(path):
            shutil.rmtree(path)

    # ── GUI app (windowed, no console) ──
    run(
        f'"{PYTHON}" -m PyInstaller --noconfirm --onefile --windowed '
        '--name "usb_relay_hw34_gui" '
        '--hidden-import customtkinter '
        '--collect-data customtkinter '
        '--collect-all serial '
        '--hidden-import PIL '
        'usb_relay_hw34_gui.py'
    )

    # ── Tray app (windowed, no console) ──
    run(
        f'"{PYTHON}" -m PyInstaller --noconfirm --onefile --windowed '
        '--name "relay_tray" '
        '--collect-all serial '
        '--hidden-import pystray '
        '--hidden-import PIL '
        'relay_tray.py'
    )

    # ── CLI tool (console) ──
    run(
        f'"{PYTHON}" -m PyInstaller --noconfirm --onefile --console '
        '--name "usb_relay_hw34_cli" '
        '--collect-all serial '
        'usb_relay_hw34_cli.py'
    )

    # ── Collect everything into dist/USB-RELAY04/ ──
    os.makedirs(DIST_DIR, exist_ok=True)

    onefile_dir = os.path.join(SCRIPT_DIR, "dist")

    for exe_name in ["usb_relay_hw34_gui.exe", "relay_tray.exe", "usb_relay_hw34_cli.exe"]:
        src = os.path.join(onefile_dir, exe_name)
        dst = os.path.join(DIST_DIR, exe_name)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"  Moved {exe_name} -> dist/USB-RELAY04/")

    # Copy config and docs
    for fname in ["relay_mapping.cfg", "README.txt", "INSTALLER_README.txt"]:
        src = os.path.join(SCRIPT_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(DIST_DIR, fname))
            print(f"  Copied {fname}")

    # Copy driver folder
    driver_src = os.path.join(SCRIPT_DIR, "Driver")
    driver_dst = os.path.join(DIST_DIR, "Driver")
    if os.path.exists(driver_src):
        if os.path.exists(driver_dst):
            shutil.rmtree(driver_dst)
        shutil.copytree(driver_src, driver_dst)
        print("  Copied Driver/")

    print(f"\n{'='*60}")
    print(f"  BUILD COMPLETE")
    print(f"  Output: {DIST_DIR}")
    print(f"{'='*60}")
    print(f"\nNext step: compile installer.iss with Inno Setup.")


if __name__ == "__main__":
    main()
