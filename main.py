import requests
import json
import os
import time

# === Configuration ===
with open("usernames.txt", "r", encoding="utf-8") as f:
    USERNAMES = [line.strip() for line in f if line.strip()]
    LOCAL_DATA_FILE = "all_user_matches.json"
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

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

# === Save data to file ===
def save_all_matches(data):
    with open(LOCAL_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Load saved data ===
def load_all_matches():
    if not os.path.exists(LOCAL_DATA_FILE):
        return {}
    with open(LOCAL_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# === Main execution ===
if __name__ == "__main__":
    all_matches = load_all_matches()  # Load existing matches if any

    print("Fetching match data for users...")
    for username in USERNAMES:
        print(f"→ Fetching matches for {username}...")

        matches = fetch_user_matches(username, count=50, includedecay=True)
        if not matches:
            print(f"✗ Failed to fetch matches for {username}.")
            continue

        existing = all_matches.get(username, {}).get("data", [])

        # Only add new matches (by ID)
        unique_new = matches.get("data", [])

        combined_matches = existing + unique_new
        all_matches[username] = {
            "status": "success",
            "data": combined_matches
        }

        print(f"✓ Added {len(unique_new)} new matches for {username}.")

    save_all_matches(all_matches)
    print(f"\nAll updated data saved to '{LOCAL_DATA_FILE}'.")

    # Optional: Summary
    for user, match_data in all_matches.items():
        print(f"{user}: {len(match_data.get('data', []))} total matches")