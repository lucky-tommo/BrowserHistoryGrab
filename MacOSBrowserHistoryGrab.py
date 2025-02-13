import sqlite3
import csv
import os
import argparse
from datetime import datetime
import subprocess

# Helper function to convert WebKit timestamp to human-readable format
def convert_time(timestamp):
    epoch_start = 978307200  # Safari epoch start (January 1, 2001)
    return datetime.fromtimestamp(timestamp + epoch_start)  # Convert seconds to human-readable format

# Function to kill browser processes
def kill_browsers():
    browser_processes = ['Google Chrome', 'firefox', 'Safari']
    for process in browser_processes:
        subprocess.run(['pkill', '-f', process])
        print(f"Terminating {process} if running")

# Function to extract Chrome history on macOS
def extract_chrome_history():
    #Managed Chrome will have a Profile folder, rather than the default - this should be "Profile 1" on non hotdesk machines. 
    #db_path = os.path.expanduser('~/Library/Application Support/Google/Chrome/Profile 1/History')
    db_path = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/History')
    print(f"Chrome history database path: {db_path}")
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

# Function to extract Firefox history on macOS
def extract_firefox_history():
    profile_path = os.path.expanduser('~/Library/Application Support/Firefox/Profiles')
    print(f"Firefox profiles path: {profile_path}")
    if not os.path.exists(profile_path):
        print("Firefox profiles not found.")
        return
    for root, dirs, files in os.walk(profile_path):
        for file in files:
            if file == 'places.sqlite':
                db_path = os.path.join(root, file)
                print(f"Firefox history database path: {db_path}")
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

# Function to extract Safari history on macOS
def extract_safari_history():
    db_path = os.path.expanduser('~/Library/Safari/History.db')
    print(f"Safari history database path: {db_path}")
    if not os.path.exists(db_path):
        print("Safari history database not found.")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, visit_time FROM history_visits JOIN history_items ON history_visits.history_item = history_items.id")
        rows = cursor.fetchall()
        with open('safari_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['URL', 'Visit Time'])
            for row in rows:
                row = list(row)
                row[1] = convert_time(row[1])
                csvwriter.writerow(row)
        conn.close()
        print("Safari history saved to safari_history.csv")
    except sqlite3.OperationalError as e:
        print(f"OperationalError: {e}")
        print("Ensure that Safari is completely closed before running this script.")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Extract browsing history from Chrome, Firefox, and Safari.")
parser.add_argument('-kill', action='store_true', help='Kill browser processes before extracting history')
args = parser.parse_args()

# Kill browsers if -kill option is specified
if args.kill:
    kill_browsers()

# Extract histories
extract_chrome_history()
extract_firefox_history()
extract_safari_history()
