import sqlite3
import csv
import os
import psutil
import argparse
import winreg
from datetime import datetime

# Helper function to convert WebKit timestamp to human-readable format
def convert_time(timestamp):
    epoch_start = 11644473600000000  # WebKit epoch start
    return datetime.fromtimestamp((timestamp - epoch_start) / 1000000)  # Convert microseconds to seconds

# Function to kill browser processes
def kill_browsers():
    browser_processes = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe']
    for process in psutil.process_iter(['name']):
        if process.info['name'].lower() in browser_processes:
            print(f"Killing process: {process.info['name']}")
            process.terminate()

# Function to extract Chrome history on Windows
def extract_chrome_history():
    db_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'History')
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

# Function to extract Edge history on Windows
def extract_edge_history():
    db_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'History')
    if not os.path.exists(db_path):
        print("Edge history database not found.")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls")
        rows = cursor.fetchall()
        with open('edge_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['URL', 'Title', 'Last Visit Time'])
            for row in rows:
                row = list(row)
                row[2] = convert_time(row[2])
                csvwriter.writerow(row)
        conn.close()
        print("Edge history saved to edge_history.csv")
    except sqlite3.OperationalError as e:
        print(f"OperationalError: {e}")
        print("Ensure that Microsoft Edge is completely closed before running this script.")

# Function to extract Firefox history on Windows
def extract_firefox_history():
    profile_path = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
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

# Function to extract Internet Explorer history on Windows
def extract_ie_history():
    try:
        ie_history_path = "HKCU\\Software\\Microsoft\\Internet Explorer\\TypedURLs"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, ie_history_path) as key:
            count = 0
            ie_history = []
            while True:
                try:
                    value = winreg.EnumValue(key, count)
                    ie_history.append(value[1])
                    count += 1
                except OSError:
                    break
        with open('ie_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['URL'])
            for url in ie_history:
                csvwriter.writerow([url])
        print("Internet Explorer history saved to ie_history.csv")
    except FileNotFoundError as e:
        print("Internet Explorer history not found.")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Extract browsing history from various browsers.")
parser.add_argument('-kill', action='store_true', help='Kill browser processes before extracting history')
args = parser.parse_args()

# Kill browsers if -kill option is specified
if args.kill:
    kill_browsers()

# Extract histories
extract_chrome_history()
extract_edge_history()
extract_firefox_history()
extract_ie_history()
