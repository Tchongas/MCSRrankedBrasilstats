# Match Stats Analyzer

A simple Python project for analyzing match data from brazilian players.

### 1. Fetch All Matches
Fetch match data for all users (Run this first):

```bash
python main.py
```

### 2. Remove Duplicate Matches
Clean up duplicate entries from the dataset:

```bash
python removedupes.py
```

### 3. Parse and Analyze Data

#### All Statistics
```bash
python parsedata.py --stat all
```

#### Individual Forfeits
```bash
python parsedata.py --stat individual_forfeits
```

#### Win Rate
```bash
python parsedata.py --stat winrate
```

#### Matches Played
```bash
python parsedata.py --stat matches
```

#### Forfeits
```bash
python parsedata.py --stat forfeits
```

#### Bastions
```bash
python parsedata.py --stat bastions
```

#### Overworlds
```bash
python parsedata.py --stat overworlds
```

---

## 📁 Project Structure

```
.
├── main.py              # Fetches match data for users
├── removedupes.py       # Removes duplicate match entries
├── parsedata.py         # Parses and analyzes match statistics
```