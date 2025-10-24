import os
import subprocess
import sys
import json
import platform
import glob
import urllib.request
import urllib.error
import time
import urllib.parse
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

FASTFLAGS_FILE = "fastFlags.json"
BOOTSTRAPPER_URL = "https://setup.pekora.zip/PekoraPlayerLauncher.exe"
BOOTSTRAPPER_FILE = "PekoraPlayerLauncher.exe"

HOME_DIR = Path.home() / ".local" / "share" / "pekora-player"
ICONS_FOLDER = Path.home() / ".local" / "share" / "icons" / "hicolor"
DESKTOP_APPS = Path.home() / ".local" / "share" / "applications"
ENTRY_FILE = DESKTOP_APPS / "pekora-player.desktop"
UNINSTALL_ENTRY_FILE = DESKTOP_APPS / "uninstall-pekora-player.desktop"

URI_KEY_ARG_MAP = {
    "launchmode": "--",
    "gameinfo": "-t",
    "placelauncherurl": "-j",
    "launchtime": "--launchtime=",
    "task": "-task",
    "placeId": "-placeId",
    "universeId": "-universeId",
    "userId": "-userId",
}

if os.name == "nt":
    import msvcrt
    def press_any_key(prompt="Press any key to continue..."):
        print(Fore.MAGENTA + prompt, end="", flush=True)
        msvcrt.getch()
        print()
else:
    def press_any_key(prompt="Press any key to continue..."):
        input(Fore.MAGENTA + prompt)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_system_info():
    system = platform.system().lower()
    return {
        'is_windows': system == 'windows',
        'is_linux': system == 'linux',
        'is_macos': system == 'darwin',
        'system_name': system
    }

def show_linux_disclaimer():
    clear()
    print(Fore.YELLOW + "=" * 60)
    print(Fore.RED + "LINUX EXPERIMENTAL SUPPORT")
    print(Fore.YELLOW + "=" * 60)
    print(Fore.CYAN + "\nkoroneStrap has detected you are on Linux.")
    print(Fore.CYAN + "Linux support is highly experimental, therefore report any")
    print(Fore.CYAN + "bugs using the Issues tab on GitHub.")
    print(Fore.YELLOW + "\nContinuing in 5 seconds...")
    print(Fore.YELLOW + "=" * 60)
    for i in range(5, 0, -1):
        print(f"\r{Fore.GREEN}[{i}]", end="", flush=True)
        time.sleep(1)
    print("\n")

def parse_uri(uri):
    params = []
    params_str = []
    year = "2017L"
    for param in uri.split("+"):
        if ":" not in param:
            continue
        key, val = param.split(":", 1)
        if key == "clientversion" and val:
            year = val
            continue
        if key not in URI_KEY_ARG_MAP or not val:
            continue
        if key == "placelauncherurl" and val:
            val = urllib.parse.unquote(val)
        arg_prefix = URI_KEY_ARG_MAP[key]
        params_str.append(f"{arg_prefix}{val}")
        if key == "launchmode":
            params.extend([f"{arg_prefix}{val}", "-a", "https://www.pekora.zip/Login/Negotiate.ashx"])
            params_str.append("-a https://www.pekora.zip/Login/Negotiate.ashx")
        else:
            params.extend([arg_prefix, val] if not arg_prefix.endswith("=") else [f"{arg_prefix}{val}"])
    return {
        'uri': params,
        'uri_string': ' '.join(params_str),
        'year': year
    }

def create_desktop_entry(script_path):
    if not get_system_info()['is_linux']:
        return
    print(Fore.CYAN + "[*] Creating Desktop Entry for Pekora Player...")
    DESKTOP_APPS.mkdir(parents=True, exist_ok=True)
    desktop_content = f"""[Desktop Entry]
Name=Pekora Player
Exec=python3 {script_path} --uri %u
Type=Application
Terminal=false
MimeType=x-scheme-handler/pekora-player
Categories=Game
Icon=pekora-player
NoDisplay=true
"""
    try:
        with open(ENTRY_FILE, 'w') as f:
            f.write(desktop_content)
        print(Fore.GREEN + f"[*] Desktop entry created: {ENTRY_FILE}")
    except Exception as e:
        print(Fore.RED + f"[!] Failed to create desktop entry: {e}")
        return
    uninstall_content = f"""[Desktop Entry]
Name=Uninstall Pekora Player
Exec=python3 {script_path} --uninstall
Type=Application
Terminal=true
Categories=Game
Icon=pekora-player
"""
    try:
        with open(UNINSTALL_ENTRY_FILE, 'w') as f:
            f.write(uninstall_content)
        print(Fore.GREEN + f"[*] Uninstall entry created: {UNINSTALL_ENTRY_FILE}")
    except Exception as e:
        print(Fore.RED + f"[!] Failed to create uninstall entry: {e}")

def register_uri_handler():
    if not get_system_info()['is_linux']:
        return
    print(Fore.CYAN + "[*] Registering MIME type handler...")
    try:
        subprocess.run(
            ["update-desktop-database", str(DESKTOP_APPS)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(Fore.GREEN + "[*] Desktop database updated")
    except Exception as e:
        print(Fore.YELLOW + f"[!] Could not update desktop database: {e}")
    try:
        subprocess.run(
            ["xdg-mime", "default", "pekora-player.desktop", "x-scheme-handler/pekora-player"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(Fore.GREEN + "[*] MIME type registered")
    except Exception as e:
        print(Fore.YELLOW + f"[!] Could not register MIME type: {e}")

def download_icon():
    if not get_system_info()['is_linux']:
        return
    print(Fore.CYAN + "[*] Downloading player icon...")
    icon_dir = ICONS_FOLDER / "96x96" / "apps"
    icon_dir.mkdir(parents=True, exist_ok=True)
    icon_path = icon_dir / "pekora-player.png"
    icon_url = "https://raw.githubusercontent.com/johnhamilcar/PekoraBootstrapperLinux/refs/heads/main/pekora-player-bootstrapper.png"
    try:
        urllib.request.urlretrieve(icon_url, str(icon_path))
        print(Fore.GREEN + f"[*] Icon installed: {icon_path}")
    except Exception as e:
        print(Fore.YELLOW + f"[!] Could not download icon: {e}")

def setup_linux_integration():
    if not get_system_info()['is_linux']:
        return
    script_path = os.path.abspath(__file__)
    create_desktop_entry(script_path)
    download_icon()
    register_uri_handler()
    print(Fore.GREEN + "[*] Linux integration setup complete!")

def uninstall_linux_integration():
    if not get_system_info()['is_linux']:
        return
    print(Fore.CYAN + "[*] Uninstalling Linux integration...")
    for entry in [ENTRY_FILE, UNINSTALL_ENTRY_FILE]:
        if entry.exists():
            try:
                entry.unlink()
                print(Fore.GREEN + f"[*] Removed: {entry}")
            except Exception as e:
                print(Fore.RED + f"[!] Failed to remove {entry}: {e}")
    icon_path = ICONS_FOLDER / "96x96" / "apps" / "pekora-player.png"
    if icon_path.exists():
        try:
            icon_path.unlink()
            print(Fore.GREEN + f"[*] Removed icon: {icon_path}")
        except Exception as e:
            print(Fore.RED + f"[!] Failed to remove icon: {e}")
    try:
        subprocess.run(
            ["xdg-mime", "uninstall", str(ENTRY_FILE)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except:
        pass
    try:
        subprocess.run(
            ["update-desktop-database", str(DESKTOP_APPS)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except:
        pass
    print(Fore.GREEN + "[*] Linux integration uninstalled!")

def handle_uri_launch(uri):
    sys_info = get_system_info()
    if not sys_info['is_linux']:
        print(Fore.RED + "[!] URI handling is only supported on Linux")
        sys.exit(1)
    print(Fore.CYAN + f"[*] Handling URI: {uri}")
    uri_cleaned = uri.replace("pekora-player://", "").replace("pekora-player:", "")
    parsed = parse_uri(uri_cleaned)
    year = parsed['year']
    args = parsed['uri']
    print(Fore.CYAN + f"[*] Client version: {year}")
    print(Fore.CYAN + f"[*] Launch arguments: {' '.join(args)}")
    fastflags = load_fastflags()
    if fastflags:
        print(Fore.CYAN + f"[*] Applying {len(fastflags)} FastFlag(s)...")
        apply_fastflags(fastflags)
    paths = get_executable_paths(year)
    exe_path = None
    for path in paths:
