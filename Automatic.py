"""
Requirements:
    pip install undetected-chromedriver selenium setuptools pyautogui pywin32
"""

import time
import os
import sys
import ctypes
import ctypes.wintypes
import subprocess
import warnings
import logging
import pyautogui
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from datetime import datetime

uc.Chrome.__del__ = lambda self: None
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)


def find_undetek_exe(directory):
    for f in os.listdir(directory):
        if f.lower().endswith(".exe") and "undetek" in f.lower():
            return os.path.join(directory, f)
    return None


def get_pin():
    exe_dir = os.path.dirname(os.path.abspath(__file__))

    options = uc.ChromeOptions()
    options.add_argument("--window-size=1280,800")
    options.add_argument("--lang=en-US")

    print("Launching undetected Chrome...")
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
                    if t: site_date = t

                if not pin:
                    el = driver.find_element(By.ID, "getpin")
                    t = el.text.strip()
                    if t: pin = t

                if not status:
                    el = driver.find_element(By.CSS_SELECTOR, "span.undetected[style*='lawngreen']")
                    t = el.text.strip()
                    if t: status = t

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
            for f in os.listdir(exe_dir):
                if f.lower().endswith(".exe") and "undetek" in f.lower():
                    try:
                        os.remove(os.path.join(exe_dir, f))
                        print(f"🗑️  Deleted outdated file: {f}")
                    except Exception as e:
                        print(f"⚠️  Could not delete {f}: {e}")

            existing_exes = {f for f in os.listdir(exe_dir) if f.lower().endswith(".exe") and "undetek" in f.lower()}

            print("\n" + "="*60)
            print("📥 A new version of undetek is required.")
            print("   The download page will now open in the browser.")
            print()
            print("   Please:")
            print("   1. Download the zip file")
            print("   2. Extract it")
            print(f"   3. Drag the .exe into:  {exe_dir}")
            print("="*60 + "\n")

            driver.get("https://undetek.com/download/download.php")

            print("Waiting for you to place a NEW undetek .exe in the directory...")
            while True:
                for f in os.listdir(exe_dir):
                    if f.lower().endswith(".exe") and "undetek" in f.lower() and f not in existing_exes:
                        exe_path = os.path.join(exe_dir, f)
                        print(f"✅ New file detected: {f}!\n")
                        break
                else:
                    time.sleep(1)
                    continue
                break

            try:
                driver.quit()
                print("🌐 Browser closed.")
            except Exception:
                pass

            try:
                subprocess.run(
                    ["powershell", "-Command", f"Unblock-File -Path '{exe_path}'"],
                    capture_output=True
                )
                print("🛡️  File unblocked.")
            except Exception as e:
                print(f"⚠️  Could not unblock file: {e}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    # Launch exe with stdin pipe so we can write directly to it
    print(f"Launching {os.path.basename(exe_path)}...")
    process = subprocess.Popen(
        exe_path,
        cwd=exe_dir,
        stdin=subprocess.PIPE,
        text=True
    )

    # Wait for the "Enter PIN:" prompt then send it via stdin
    print("Waiting for PIN prompt...")
    time.sleep(3)

    process.stdin.write(pin + "\n")
    process.stdin.flush()
    print("PIN sent.")

    process.wait()

    exe_name = os.path.basename(exe_path)
    subprocess.run(["taskkill", "/F", "/IM", exe_name], capture_output=True)


if __name__ == "__main__":
    get_pin()