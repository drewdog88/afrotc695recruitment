import sys
import json
import zipfile
import io
from typing import Dict, Any

try:
    import requests
except Exception as e:
    print(f"ERROR: requests not available: {e}")
    sys.exit(1)


def summarize_backup(data: bytes) -> Dict[str, Any]:
    try:
        obj = json.loads(data.decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": f"invalid json: {e}"}

    tables = obj.get("tables", {})
    counts = {name: (len(rows) if isinstance(rows, list) else 0) for name, rows in tables.items()}
    return {
        "ok": True,
        "timestamp": obj.get("timestamp"),
        "backup_type": obj.get("backup_type"),
        "description": obj.get("description"),
        "counts": counts,
        "total": sum(counts.values()),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_backup_url.py <backup_zip_url>")
        sys.exit(2)

    url = sys.argv[1]
    resp = requests.get(url, timeout=60)
    if resp.status_code != 200:
        print(f"ERROR: HTTP {resp.status_code} fetching {url}")
        sys.exit(3)

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    name = None
    # Prefer 'database_backup.json' if present
    if "database_backup.json" in zf.namelist():
        name = "database_backup.json"
    else:
        # Fallback: take first json file
        for n in zf.namelist():
            if n.lower().endswith('.json'):
                name = n
                break
    if not name:
        print("ERROR: No JSON found inside ZIP")
        sys.exit(4)

    data = zf.read(name)
    summary = summarize_backup(data)
    if not summary.get("ok"):
        print(f"ERROR: {summary.get('error')}")
        sys.exit(5)

    counts = summary.get("counts", {})
    print(f"timestamp={summary.get('timestamp')} backup_type={summary.get('backup_type')} description={summary.get('description')}")
    # Print counts in stable order
    keys = [
        "user",
        "cadet",
        "potential_recruit",
        "university_contact",
        "recruitment_event",
        "external_link",
        "recruitment_document",
        "activity_log",
        "password_history",
    ]
    for k in keys:
        if k in counts:
            print(f"{k}: {counts[k]}")
    # Also print any extra tables
    for k, v in counts.items():
        if k not in keys:
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
