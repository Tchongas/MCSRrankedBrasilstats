import json
from collections import Counter
from typing import Dict, Callable
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("--stat", help="Which stat to show (or 'all')")
args = parser.parse_args()  

DATA_FILE = "all_user_matches.json"

# === Utility Functions ===

def load_data(filename=DATA_FILE) -> dict:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

# === Stat Counter Functions ===

def count_bastion_types(data: dict) -> Counter:
    VALID_TYPES = {"HOUSING", "STABLES", "TREASURE", "BRIDGE"}
    counter = Counter()

    for user_data in data.values():
        matches = user_data.get("data", [])
        for match in matches:
            bastion_type = match.get("seed", {}).get("bastion")
            if bastion_type in VALID_TYPES:
                counter[bastion_type] += 1

    return counter

def count_overworld_types(data: dict) -> Counter:
    counter = Counter()
    for user_data in data.values():
        matches = user_data.get("data", [])
        for match in matches:
            ow = match.get("seed", {}).get("overworld")
            if ow:
                counter[ow] += 1

    return counter

def count_all_matches(data: dict) -> Counter:
    counter = Counter()
    for user_data in data.values():
        matches = user_data.get("data", [])
        for match in matches:
            counter["Matches"] += 1

    return counter

def count_forfeited_matches(data: dict) -> Counter:
    counter = Counter()

    for user_data in data.values():
        matches = user_data.get("data", [])
        for match in matches:
            if match.get("forfeited") is not True:
                continue
            counter["Total Forfeits"] += 1
            players = match.get("players", [])
            changes = match.get("changes", [])

            # Find the Brazilian player (there might be only one)
            br_player = next((p for p in players if p.get("country") == "br"), None)
            if not br_player:
                continue

            br_uuid = br_player.get("uuid")

            # Check if they lost ELO
            for change in changes:
                if change.get("uuid") == br_uuid:
                    elo_change = change.get("change")
                    if isinstance(elo_change, (int, float)) and elo_change < 0:
                        counter["Brazilian Forfeits"] += 1
                        break

    return counter

def count_bastion_overworld_winrate(data: dict) -> dict:
    stats = {}  # {("HOUSING", "SHIPWRECK"): {"wins": 0, "total": 0}}

    for user_data in data.values():
        matches = user_data.get("data", [])
        for match in matches:
            seed = match.get("seed", {})
            bastion = seed.get("bastion")
            overworld = seed.get("overworld")

            if not bastion or not overworld:
                continue

            key = (bastion, overworld)

            players = match.get("players", [])
            result = match.get("result", {})
            winner_uuid = result.get("uuid")

            # Find the Brazilian player
            br_player = next((p for p in players if p.get("country") == "br"), None)
            if not br_player:
                continue

            br_uuid = br_player.get("uuid")

            if key not in stats:
                stats[key] = {"wins": 0, "total": 0}

            stats[key]["total"] += 1
            if br_uuid == winner_uuid:
                stats[key]["wins"] += 1

    return stats

def count_individual_player_forfeits(data: dict) -> dict:
    forfeits_by_player = defaultdict(lambda: {"forfeits": 0, "total": 0, "totalFFs": 0})
    
    for user_data in data.values():
        matches = user_data.get("data", [])
        for match in matches:
            players = match.get("players", [])
            changes = match.get("changes", [])
            
            # Look for BR player
            br_player = next((p for p in players if p.get("country") == "br"), None)
            if not br_player:
                continue

            name = br_player.get("nickname", "Unknown")
            br_uuid = br_player.get("uuid")
            forfeited = match.get("forfeited") is True

            # Always count total matches with this BR player
            forfeits_by_player[name]["total"] += 1

            # If forfeited and lost ELO, count it as a forfeit
            if forfeited:
                for change in changes:
                    if change.get("uuid") == br_uuid:
                        elo_change = change.get("change")
                        if isinstance(elo_change, (int, float)) and elo_change < 0:
                            forfeits_by_player[name]["forfeits"] += 1
                            break
                        else:
                            forfeits_by_player[name]["totalFFs"] += 1
                            break

    return forfeits_by_player
    

# === General-purpose Printer ===
def print_counter(title: str, counter: Counter):
    from colorama import Fore, Style
    print(f"\n{Style.BRIGHT}{title}{Style.RESET_ALL}")
    for key, count in counter.most_common():
        print(f"{Style.BRIGHT}•{Style.RESET_ALL} {key}: {Style.BRIGHT}{count}{Style.RESET_ALL}")

# === Winrate Printer ===
def print_winrates(title: str, stats: dict):
    from colorama import Fore, Style
    print(f"\n{Style.BRIGHT}{title}{Style.RESET_ALL}")
    for (bastion, overworld), values in sorted(stats.items(), key=lambda x: x[1]["total"], reverse=True):
        wins = values["wins"]
        total = values["total"]
        rate = (wins / total) * 100 if total else 0

        color = (
            Fore.GREEN if rate >= 50 else
            Fore.YELLOW if rate >= 45 else
            Fore.RED
        )

        print(f"• {bastion:10} | {overworld:15} → {color}{wins}/{total} wins ({rate:.1f}%)" + Style.RESET_ALL)

# === Individual Forfeits Printer ===
def print_individual_player_forfeits(forfeit_data: dict):
    print("\nIndividual Brazilian Forfeits")
    print("Player           | FF by player / FF by Oponent / Total Matches")
    print("-" * 40)
    for player, stats in sorted(forfeit_data.items(), key=lambda x: -x[1]["forfeits"]):
        forfeits = stats["forfeits"]
        total = stats["total"]
        totalffs = stats["totalFFs"]
        print(f"{player:15} | {forfeits}/{totalffs}/{total}")


# === Registry of all stats to run ===

STAT_COUNTERS: Dict[str, Callable[[dict], Counter]] = {
    "Bastions Count": count_bastion_types,
    "Overworlds Counts": count_overworld_types,
    "All Matches": count_all_matches,
    "Forfeits": count_forfeited_matches,
    "Individual Forfeits (Last 50 Matches)": count_individual_player_forfeits,
}

# === Main Runner ===

def main():
    parser = argparse.ArgumentParser(description="Analyze MCSR match data")
    parser.add_argument(
        "--stat",
        type=str,
        help="Which stat to show (use 'all' to print everything)",
        default="all"
    )
    args = parser.parse_args()

    data = load_data()

    stat_query = args.stat.lower()

    if stat_query == "all":
        for stat_name, func in STAT_COUNTERS.items():
            print_counter(stat_name, func(data))
        print_winrates("Brazilian Winrate by Bastion and Overworld", count_bastion_overworld_winrate(data))

    elif stat_query in ["winrate", "bastion_winrate"]:
        print_winrates("Brazilian Winrate by Bastion and Overworld", count_bastion_overworld_winrate(data))

    elif stat_query in ["individual_forfeits", "player_forfeits"]:
        result = count_individual_player_forfeits(data)
        print_individual_player_forfeits(result)

    else:
        # Try partial match in STAT_COUNTERS keys
        matched_key = next(
            (key for key in STAT_COUNTERS if stat_query in key.lower()),
            None
        )

        if matched_key:
            print_counter(matched_key, STAT_COUNTERS[matched_key](data))
        else:
            print(f"Unknown stat: '{args.stat}'\nAvailable options are:")
            for key in list(STAT_COUNTERS.keys()) + ["winrate"]:
                print(f"• {key}")

if __name__ == "__main__":
    main()