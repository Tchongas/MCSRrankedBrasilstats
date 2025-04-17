# Match Stats Analyzer

A simple Python project for analyzing match data from brazilian players.

### Fetch All Matches
Fetch match data for all users (Run this first):

```bash
python main.py
```
### Usage Examples

```bash
python query.py "SELECT * FROM matches WHERE forfeited = 1"
```

```bash
python query.py "SELECT * FROM matches WHERE forfeited = 1 AND seed_type = 'BURIED_TREASURE'"
```


---

## 📁 Project Structure

```
.
├── main.py              # Fetches match data for users
├── query.py             # Executes SQL queries on the database, Usage example: python query.py "SELECT * FROM matches WHERE forfeited = 1"
├── usernames.txt        # List of usernames to fetch data for
```