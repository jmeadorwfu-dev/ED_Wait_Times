import csv
import os
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

URL = "https://www.sentara.com/hospitalslocations/sentara-rmh-medical-center/medical-services/Sentara-RMH-Medical-Center-Emergency-Department"
OUTPUT = "ed_wait_times.csv"

def get_text():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(5000)
        text = page.inner_text("body")
        browser.close()
    return text

def extract(text):
    m = re.search(r"(\d+)\s*(?:min|minute)", text, re.IGNORECASE)
    return m.group(1) if m else ""

def main():
    text = get_text()
    wait = extract(text)
    ts = datetime.now(timezone.utc).isoformat()

    write_header = not os.path.exists(OUTPUT)
    with open(OUTPUT, "a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(["timestamp_utc", "wait_minutes", "raw_found"])
        w.writerow([ts, wait, bool(wait)])

    print(f"{ts}  wait={wait or 'NOT FOUND'}")

if __name__ == "__main__":
    main()
