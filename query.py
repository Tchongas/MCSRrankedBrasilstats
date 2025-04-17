import sqlite3
import sys
from tabulate import tabulate


DB_FILE = "matches.db"

def main():
    if len(sys.argv) < 2:
        print("Usage: python query.py \"<SQL_QUERY>\"")
        sys.exit(1)

    query = sys.argv[1]

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute(query)
        rows = cursor.fetchall()

        # Print column names
        columns = [description[0] for description in cursor.description]

        print(tabulate(rows, headers=columns, tablefmt="grid"))

        # Print rows

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
