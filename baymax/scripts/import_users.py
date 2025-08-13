import csv
import json
import os
import sys
from typing import Dict, List

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "users.json")


def ensure_data():
    data_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": []}, f, indent=2)


def load_users() -> Dict:
    ensure_data()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(doc: Dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)


def parse_schedule(s: str) -> List[Dict[str, str]]:
    s = s.strip()
    if not s:
        return []
    result: List[Dict[str, str]] = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        sub = part.split(":")
        if len(sub) >= 2:
            hh, mm = sub[0], sub[1]
            label = ":".join(sub[2:]) if len(sub) > 2 else "Medicine"
            result.append({"time": f"{int(hh):02d}:{int(mm):02d}", "label": label})
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.import_users <users.csv>")
        print("CSV columns: name,schedule (e.g., '08:00:Vitamin C, 20:00:BP')")
        sys.exit(1)
    csv_path = sys.argv[1]
    doc = load_users()
    from uuid import uuid4
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            schedule = parse_schedule(row.get("schedule", ""))
            if not name:
                continue
            record = {"id": str(uuid4()), "name": name, "schedule": schedule}
            doc["users"].append(record)
            faces_dir = os.path.join(BASE_DIR, "data", "faces", record["id"]) 
            os.makedirs(faces_dir, exist_ok=True)
            print(f"Added user: {name} ({record['id']}) with {len(schedule)} schedule items")
    save_users(doc)


if __name__ == "__main__":
    main()