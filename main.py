import requests
import json
import os
import time
import sqlite3

# === Configuration ===
with open("usernames.txt", "r", encoding="utf-8") as f:
    USERNAMES = [line.strip() for line in f if line.strip()]

DB_FILE = "matches.db"
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

# === SQLite Setup ===
def setup_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            username TEXT,
            category TEXT,
            game_mode TEXT,
            forfeited BOOLEAN,
            result_uuid TEXT,
            result_time INTEGER,
            season INTEGER,
            date INTEGER,
            seed_type TEXT,
            bastion_type TEXT
        )
    ''')
    conn.commit()
    return conn

# === Fetch data from API with retry on failure ===
def fetch_user_matches(identifier, page=0, count=50, match_type=2, tag=None, season=None, includedecay=False):
    base_url = f"https://mcsrranked.com/api/users/{identifier}/matches"
    params = {
        "page": page,
        "count": count
    }

    if match_type:
        params["type"] = match_type
    if tag:
        params["tag"] = tag
    if season:
        params["season"] = season
    if includedecay:
        params["includedecay"] = ""  # Just adding the key is enough

    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"[{identifier}] Rate limited. Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
                retries += 1
            else:
                print(f"[{identifier}] Error: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[{identifier}] Request error: {e}")
            time.sleep(RETRY_DELAY)
            retries += 1
    return None

# === Save matches to SQLite ===
def insert_matches(conn, username, match_list):
    c = conn.cursor()
    new_count = 0
    for match in match_list:
        try:
            c.execute('''
                INSERT OR IGNORE INTO matches (
                    id, username, category, game_mode, forfeited,
                    result_uuid, result_time, season, date,
                    seed_type, bastion_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match.get("id"),
                username,
                match.get("category"),
                match.get("gameMode"),
                match.get("forfeited", False),
                match.get("result", {}).get("uuid"),
                match.get("result", {}).get("time"),
                match.get("season"),
                match.get("date"),
                match.get("seedType"),
                match.get("bastionType")
            ))
            if c.rowcount:
                new_count += 1
        except Exception as e:
            print(f"✗ Error inserting match {match.get('id')}: {e}")
    conn.commit()
    return new_count


# === Main execution ===
if __name__ == "__main__":
    conn = setup_database()

    print("Fetching match data for users...")
    for username in USERNAMES:
        print(f"→ Fetching matches for {username}...")

        matches = fetch_user_matches(username, count=50, includedecay=True)
        if not matches:
            print(f"✗ Failed to fetch matches for {username}.")
            continue

        new_matches = matches.get("data", [])
        added = insert_matches(conn, username, new_matches)

        print(f"✓ Added {added} new matches for {username}.")

    conn.close()
    print(f"\nAll match data saved to SQLite database '{DB_FILE}'.")
