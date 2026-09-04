from database.db import initialize_database
from database.log_repository import (
    store_upload_results,
    get_all_logs,
    get_log_by_id
)


# ============================================================
# 1. INITIALIZE DATABASE
# ============================================================

initialize_database()


# ============================================================
# 2. SAMPLE RESULTS
# Simulates Member 1's /upload endpoint output
# ============================================================

sample_results = [

    {
        "format": "json",
        "fields": {
            "event": "login",
            "user": "alice"
        },
        "raw": '{"event": "login", "user": "alice"}',
        "confidence": "high"
    },

    {
        "format": "csv",
        "fields": [
            "alice",
            "login",
            "2026-09-03"
        ],
        "raw": "alice,login,2026-09-03",
        "confidence": "high"
    },

    {
        "format": "text",
        "fields": {
            "timestamp": "2026-09-03 10:30:22",
            "level": "INFO",
            "message": "Server started"
        },
        "raw": "2026-09-03 10:30:22 INFO Server started",
        "confidence": "medium"
    },

    {
        "format": "unknown_pattern",
        "fields": {
            "template": "Connection from <*> failed"
        },
        "raw": "Connection from 192.168.1.25 failed",
        "confidence": "low"
    }
]


# ============================================================
# 3. STORE THE COMPLETE UPLOAD
# ============================================================

print("\nStoring complete upload...\n")

stored_log_ids = store_upload_results(
    "sample_log.txt",
    sample_results
)


print("Upload stored successfully!")

for log_id in stored_log_ids:
    print("Stored Log ID:", log_id)


# ============================================================
# 4. RETRIEVE ONE OF THE NEWLY STORED LOGS
# ============================================================

print("\n" + "=" * 60)
print("VERIFYING ONE STORED LOG")
print("=" * 60)

first_log = get_log_by_id(stored_log_ids[0])

if first_log:
    print("Log found:")
    print(first_log)
else:
    print("Log not found.")


# ============================================================
# 5. SHOW TOTAL DATABASE RECORDS
# ============================================================

print("\n" + "=" * 60)
print("ALL STORED LOGS")
print("=" * 60)

logs = get_all_logs()

print("Total logs in database:", len(logs))