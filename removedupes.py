import json

def remove_global_duplicates_by_id(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    seen_ids = set()
    duplicate_ids = set()
    total_removed = 0

    for player, player_data in data.items():
        if "data" not in player_data:
            continue

        unique_matches = []
        for match in player_data["data"]:
            match_id = match.get("id")
            if match_id is None:
                unique_matches.append(match)  # Keep malformed matches
                continue

            if match_id in seen_ids:
                print(f"Duplicate match found and removed: ID {match_id}")
                duplicate_ids.add(match_id)
                total_removed += 1
                continue

            seen_ids.add(match_id)
            unique_matches.append(match)

        player_data["data"] = unique_matches

    # Save cleaned data back to the original file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Done. Removed {total_removed} duplicate matches (based on ID).")

# Run it
if __name__ == "__main__":
    remove_global_duplicates_by_id("all_user_matches.json")
