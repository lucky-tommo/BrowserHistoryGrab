import sqlite3
import csv
import os
import argparse
from datetime import datetime
import subprocess

# Helper function to convert WebKit timestamp to human-readable format
def convert_time(timestamp):
    epoch_start = 11644473600000000  # WebKit epoch start
    return datetime.fromtimestamp((timestamp - epoch_start) / 1000000)  # Convert microseconds to seconds

# Function to kill browser processes
def kill_browsers():
    browser_processes = ['chrome', 'firefox']
    for process in browser_processes:
        subprocess.run(['pkill', '-f', process])
        print(f"Terminating {process} if running")

# Function to extract Chrome history on Linux
def extract_chrome_history():
    db_path = os.path.expanduser('~/.config/google-chrome/Default/History')
    if not os.path.exists(db_path):
        print("Chrome history database not found.")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls")
        rows = cursor.fetchall()
        with open('chrome_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['URL', 'Title', 'Last Visit Time'])
            for row in rows:
                row = list(row)
                row[2] = convert_time(row[2])
                csvwriter.writerow(row)
        conn.close()
        print("Chrome history saved to chrome_history.csv")
    except sqlite3.OperationalError as e:
        print(f"OperationalError: {e}")
        print("Ensure that Google Chrome is completely closed before running this script.")

# Function to extract Firefox history on Linux
def extract_firefox_history():
    profile_path = os.path.expanduser('~/.mozilla/firefox')
    if not os.path.exists(profile_path):
        print("Firefox profiles not found.")
        return
    for root, dirs, files in os.walk(profile_path):
        for file in files:
            if file == 'places.sqlite':
                db_path = os.path.join(root, file)
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT url, title, visit_date FROM moz_places")
                    rows = cursor.fetchall()
                    with open('firefox_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(['URL', 'Title', 'Visit Date'])
                        for row in rows:
                            row = list(row)
                            row[2] = datetime.fromtimestamp(row[2] / 1000000)
                            csvwriter.writerow(row)
                    conn.close()
                    print("Firefox history saved to firefox_history.csv")
                except sqlite3.OperationalError as e:
                    print(f"OperationalError: {e}")
                    print("Ensure that Firefox is completely closed before running this script.")
                break

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Extract browsing history from Firefox and Chrome.")
parser.add_argument('-kill', action='store_true', help='Kill browser processes before extracting history')
args = parser.parse_args()

# Kill browsers if -kill option is specified
if args.kill:
    kill_browsers()

# Extract histories
extract_chrome_history()
extract_firefox_history()
