import os
import json
import zipfile
import io
from datetime import datetime

try:
	from dotenv import load_dotenv
except Exception:
	load_dotenv = None


def load_env():
	# Load env from .env and env.local if available
	if load_dotenv is not None:
		# Load default .env first, then overlay env.local
		load_dotenv()
		if os.path.exists("env.local"):
			                   load_dotenv()


def summarize_backup_json_bytes(data: bytes):
	try:
		obj = json.loads(data.decode("utf-8"))
	except Exception:
		return {"ok": False, "error": "invalid json"}

	tables = obj.get("tables", {})
	counts = {name: (len(rows) if isinstance(rows, list) else 0) for name, rows in tables.items()}
	return {
		"ok": True,
		"timestamp": obj.get("timestamp"),
		"backup_type": obj.get("backup_type", "daily"),
		"description": obj.get("description", ""),
		"counts": counts,
		"total": sum(counts.values())
	}


def main():
	load_env()

	# Import after env is loaded so vercel_blob picks up credentials
	import neon_backup_scheduler as n

	files = n.list_backup_files()
	results = []
	for f in files:
		name = f.get("filename")
		if not name:
			continue
		meta = {"filename": name, "backup_type": f.get("backup_type"), "created": f.get("created"), "description": f.get("description")}
		try:
			content = n.download_backup_file(name)
			if not content:
				meta["ok"] = False
				meta["reason"] = "download_failed"
				results.append(meta)
				continue

			if name.endswith(".json"):
				summary = summarize_backup_json_bytes(content)
				meta.update(summary)
			elif name.endswith(".zip"):
				# Try to extract database_backup.json
				try:
					zf = zipfile.ZipFile(io.BytesIO(content))
					if "database_backup.json" in zf.namelist():
						json_bytes = zf.read("database_backup.json")
						summary = summarize_backup_json_bytes(json_bytes)
						meta.update(summary)
					else:
						meta["ok"] = False
						meta["reason"] = "no_database_backup_json"
				except Exception as e:
					meta["ok"] = False
					meta["reason"] = f"zip_error:{e}"
			else:
				meta["ok"] = False
				meta["reason"] = "unknown_extension"
		except Exception as e:
			meta["ok"] = False
			meta["reason"] = f"error:{e}"
		results.append(meta)

	# Sort by total rows desc, then by created desc
	def created_key(v):
		c = v.get("created")
		return c if isinstance(c, datetime) else datetime.min

	results.sort(key=lambda v: (v.get("total", 0), created_key(v)), reverse=True)

	# Print concise summary lines
	for r in results:
		created = r.get("created")
		created_str = created.isoformat() if isinstance(created, datetime) else ""
		total = r.get("total", 0)
		counts = r.get("counts") or {}
		key_counts = {k: v for k, v in counts.items() if v}
		print(f"{r.get('filename')} | type={r.get('backup_type')} | created={created_str} | total={total} | non_empty={key_counts}")


if __name__ == "__main__":
	main()


