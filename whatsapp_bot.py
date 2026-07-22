"""
WhatsApp Web Message Sender

Sends a message to contacts listed in contacts.json via WhatsApp Web.
Uses Selenium with automatic ChromeDriver management (no manual download needed).

Usage:
    python whatsapp_bot.py
    python whatsapp_bot.py --message "Hello everyone!"
    python whatsapp_bot.py --contacts my_contacts.json
"""

import argparse
import json
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("Error: webdriver-manager not installed.")
    print("  pip install webdriver-manager")
    sys.exit(1)


CONTACTS_FILE = "contacts.json"
WHATSAPP_URL = "https://web.whatsapp.com"
DEFAULT_MESSAGE = "Hello! This is an automated message."


def load_contacts(filepath):
    """Load contacts from JSON file."""
    if not os.path.exists(filepath):
        print(f"Error: Contacts file not found: {filepath}")
        print(f"Create it with this format:")
        print(json.dumps({"contacts": [{"name": "John", "number": "+1234567890"}]}, indent=2))
        sys.exit(1)

    with open(filepath) as f:
        data = json.load(f)

    contacts = data.get("contacts", [])
    if not contacts:
        print("Error: No contacts found in file.")
        sys.exit(1)

    return contacts


def create_driver():
    """Create Chrome WebDriver with automatic driver management."""
    options = Options()
    # Keep browser open for QR scan
    options.add_experimental_option("detach", True)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Auto-download correct ChromeDriver version
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def wait_for_login(driver, timeout=120):
    """Wait for user to scan QR code and log in."""
    print("\n📱 Scan the QR code with your phone to log in...")
    print(f"   Waiting up to {timeout} seconds...\n")

    try:
        # Wait until the search box appears (indicates login complete)
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        print("✅ Logged in successfully!\n")
        return True
    except Exception:
        print("❌ Login timeout. Please try again.")
        return False


def send_message(driver, contact_name, message, delay=3):
    """Send a message to a contact by searching their name."""
    try:
        # Click search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        search_box.click()
        time.sleep(0.5)

        # Type contact name
        search_box.clear()
        search_box.send_keys(contact_name)
        time.sleep(2)

        # Click on the contact
        try:
            contact = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]'))
            )
            contact.click()
            time.sleep(1)
        except Exception:
            print(f"  ⚠ Contact '{contact_name}' not found. Skipping.")
            # Clear search
            search_box.send_keys(Keys.ESCAPE)
            return False

        # Type and send message
        msg_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        msg_box.click()
        msg_box.send_keys(message)
        msg_box.send_keys(Keys.ENTER)

        print(f"  ✅ Sent to {contact_name}")
        time.sleep(delay)
        return True

    except Exception as e:
        print(f"  ❌ Failed to send to {contact_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send WhatsApp messages via WhatsApp Web")
    parser.add_argument("--message", "-m", default=DEFAULT_MESSAGE, help="Message to send")
    parser.add_argument("--contacts", "-c", default=CONTACTS_FILE, help="Path to contacts JSON file")
    parser.add_argument("--delay", type=int, default=3, help="Seconds between messages (default: 3)")
    args = parser.parse_args()

    contacts = load_contacts(args.contacts)

    print("🤖 WhatsApp Bot")
    print(f"   Contacts: {len(contacts)}")
    print(f"   Message: \"{args.message[:50]}{'...' if len(args.message) > 50 else ''}\"")

    driver = create_driver()
    driver.get(WHATSAPP_URL)

    if not wait_for_login(driver):
        driver.quit()
        sys.exit(1)

    # Send messages
    sent = 0
    failed = 0
    for contact in contacts:
        name = contact.get("name", "")
        if not name:
            continue

        success = send_message(driver, name, args.message, delay=args.delay)
        if success:
            sent += 1
        else:
            failed += 1

    print(f"\nDone: {sent} sent, {failed} failed.")
    print("Browser will remain open. Close it manually when done.")


if __name__ == "__main__":
    main()
