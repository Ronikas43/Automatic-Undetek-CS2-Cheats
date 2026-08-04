"""
Requirements:
    pip install undetected-chromedriver selenium setuptools pyautogui
"""

import time
import os
import sys
import shutil
import zipfile
import subprocess
import warnings
import logging
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from datetime import datetime

uc.Chrome.__del__ = lambda self: None
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)


def get_chrome_major_version():
    """Detect installed Chrome version on Windows."""
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                result = subprocess.run(
                    ["powershell", "-Command",
                     f"(Get-Item '{path}').VersionInfo.ProductVersion"],
                    capture_output=True, text=True
                )
                version_str = result.stdout.strip()
                major = int(version_str.split(".")[0])
                print(f"🌐 Detected Chrome version: {version_str} (major: {major})")
                return major
            except Exception:
                pass
    return None


def find_undetek_exe(directory):
    for f in os.listdir(directory):
        if f.lower().endswith(".exe") and "undetek" in f.lower():
            return os.path.join(directory, f)
    return None


def delete_undetek_exes(directory):
    for f in os.listdir(directory):
        if f.lower().endswith(".exe") and "undetek" in f.lower():
            try:
                os.remove(os.path.join(directory, f))
                print(f"🗑️  Deleted: {f}")
            except Exception as e:
                print(f"⚠️  Could not delete {f}: {e}")


def extract_and_place_exe(zip_path, dest_dir):
    extract_tmp = os.path.join(dest_dir, "_undetek_extract_tmp")
    if os.path.exists(extract_tmp):
        shutil.rmtree(extract_tmp, ignore_errors=True)
    os.makedirs(extract_tmp, exist_ok=True)

    try:
        print(f"📦 Extracting {os.path.basename(zip_path)}...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_tmp)
    except Exception as e:
        print(f"❌ Failed to extract zip: {e}")
        shutil.rmtree(extract_tmp, ignore_errors=True)
        return None

    found_exe = None
    for root, dirs, files in os.walk(extract_tmp):
        for fname in files:
            if fname.lower().endswith(".exe") and "undetek" in fname.lower():
                found_exe = os.path.join(root, fname)
                break
        if found_exe:
            break

    if not found_exe:
        print("❌ No undetek .exe found inside the zip.")
        shutil.rmtree(extract_tmp, ignore_errors=True)
        return None

    dest_exe = os.path.join(dest_dir, os.path.basename(found_exe))
    shutil.move(found_exe, dest_exe)
    print(f"✅ Placed exe: {os.path.basename(dest_exe)}")

    shutil.rmtree(extract_tmp, ignore_errors=True)
    print("🧹 Cleaned up extracted folders.")

    try:
        os.remove(zip_path)
        print(f"🗑️  Deleted zip: {os.path.basename(zip_path)}")
    except Exception as e:
        print(f"⚠️  Could not delete zip: {e}")

    return dest_exe


def wait_for_new_zip(directory, existing_zips, timeout=300):
    print("⏳ Waiting for zip download to complete...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        for f in os.listdir(directory):
            full = os.path.join(directory, f)
            if (
                f.lower().endswith(".zip")
                and "undetek" in f.lower()
                and full not in existing_zips
                and not f.endswith(".crdownload")
                and not f.endswith(".part")
            ):
                time.sleep(1)
                return full
        time.sleep(0.5)
    return None


def get_pin():
    exe_dir = os.path.dirname(os.path.abspath(__file__))

    options = uc.ChromeOptions()
    options.add_argument("--window-size=1280,800")
    options.add_argument("--lang=en-US")
    prefs = {
        "download.default_directory": exe_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    # Auto-detect Chrome version to avoid ChromeDriver mismatch
    chrome_version = get_chrome_major_version()

    print("Launching undetected Chrome...")
    if chrome_version:
        driver = uc.Chrome(options=options, headless=False, version_main=chrome_version)
    else:
        driver = uc.Chrome(options=options, headless=False)

    try:
        print("Navigating to page...")
        driver.get("https://undetek.com/free-cs2-cheats-download/")

        print("Waiting for page to load...")
        pin = site_date = status = None

        while True:
            try:
                if not site_date:
                    el = driver.find_element(By.ID, "date-display")
                    t = el.text.strip()
                    if t:
                        site_date = t

                if not pin:
                    el = driver.find_element(By.ID, "getpin")
                    t = el.text.strip()
                    if t:
                        pin = t

                if not status:
                    el = driver.find_element(By.CSS_SELECTOR, "span.undetected[style*='lawngreen']")
                    t = el.text.strip()
                    if t:
                        status = t

                if pin and site_date and status:
                    break
            except Exception:
                pass
            time.sleep(0.5)

        print(f"📅 Site date:  {site_date}")
        print(f"🔒 Status:     {status}")
        print(f"🔑 PIN Code:   {pin}")

        if status != "Undetekted":
            print(f"\n❌ Status is '{status}' — not safe to inject. Closing.")
            driver.quit()
            sys.exit(1)
        print("✅ Status is Undetekted — safe to continue.\n")

        parsed_site_date = None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%B %d, %Y", "%d %B %Y", "%d-%m-%Y"):
            try:
                parsed_site_date = datetime.strptime(site_date, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
        if not parsed_site_date:
            parsed_site_date = site_date

        exe_path = find_undetek_exe(exe_dir)
        needs_download = False

        if not exe_path:
            print("⚠️  No undetek .exe found in current directory.")
            needs_download = True
        else:
            exe_date = datetime.fromtimestamp(os.path.getmtime(exe_path)).strftime("%Y-%m-%d")
            print(f"📁 Found: {os.path.basename(exe_path)} (modified: {exe_date})")
            if exe_date != parsed_site_date:
                print(f"⚠️  Date mismatch! Site: '{parsed_site_date}', Local: '{exe_date}'.")
                needs_download = True
            else:
                print("✅ File is up to date.\n")

        if needs_download:
            print("🗑️  Removing outdated undetek exe(s)...")
            delete_undetek_exes(exe_dir)

            existing_zips = {
                os.path.join(exe_dir, f)
                for f in os.listdir(exe_dir)
                if f.lower().endswith(".zip")
            }

            print("\n" + "=" * 60)
            print("📥 Downloading new undetek version automatically...")
            print("=" * 60 + "\n")

            driver.get("https://undetek.com/download/download.php")

            zip_path = wait_for_new_zip(exe_dir, existing_zips, timeout=120)

            if not zip_path:
                print("❌ Zip download timed out. Please download manually and re-run.")
                driver.quit()
                sys.exit(1)

            print(f"✅ Download detected: {os.path.basename(zip_path)}\n")

            try:
                driver.quit()
                print("🌐 Browser closed.")
            except Exception:
                pass

            exe_path = extract_and_place_exe(zip_path, exe_dir)

            if not exe_path:
                print("❌ Could not find exe after extraction. Please extract manually.")
                sys.exit(1)

            try:
                subprocess.run(
                    ["powershell", "-Command", f"Unblock-File -Path '{exe_path}'"],
                    capture_output=True,
                )
                print("🛡️  File unblocked.\n")
            except Exception as e:
                print(f"⚠️  Could not unblock file: {e}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    print(f"🚀 Launching {os.path.basename(exe_path)}...")
    process = subprocess.Popen(
        exe_path,
        cwd=exe_dir,
        stdin=subprocess.PIPE,
        text=True,
    )

    print("⏳ Waiting for PIN prompt...")
    time.sleep(3)

    process.stdin.write(pin + "\n")
    process.stdin.flush()

    process.wait()

    exe_name = os.path.basename(exe_path)
    subprocess.run(["taskkill", "/F", "/IM", exe_name], capture_output=True)


if __name__ == "__main__":
    get_pin()