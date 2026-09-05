from processors.normalizer import normalize_log


# =========================================================
# TEST 1: JSON LOG
# =========================================================

json_result = {
    "format": "json",
    "fields": {
        "event": "login",
        "user": "alice"
    },
    "raw": '{"event": "login", "user": "alice"}',
    "confidence": "high"
}


# =========================================================
# TEST 2: CSV LOG
# =========================================================

csv_result = {
    "format": "csv",
    "fields": [
        "alice",
        "login",
        "2026-09-03"
    ],
    "raw": "alice,login,2026-09-03",
    "confidence": "high"
}


# =========================================================
# TEST 3: TEXT LOG
# =========================================================

text_result = {
    "format": "text",
    "fields": {
        "timestamp": "2026-09-03 10:30:22",
        "level": "INFO",
        "message": "Server started"
    },
    "raw": "2026-09-03 10:30:22 INFO Server started",
    "confidence": "medium"
}


# =========================================================
# TEST 4: UNKNOWN LOG
# =========================================================

unknown_result = {
    "format": "unknown_pattern",
    "fields": {
        "template": "Connection from <*> failed"
    },
    "raw": "Connection from 192.168.1.25 failed",
    "confidence": "low"
}


# =========================================================
# NORMALIZE AND PRINT
# =========================================================

print("\nJSON NORMALIZED EVENT:")
print(normalize_log(json_result, "sample_log.txt"))


print("\nCSV NORMALIZED EVENT:")
print(normalize_log(csv_result, "sample_log.txt"))


print("\nTEXT NORMALIZED EVENT:")
print(normalize_log(text_result, "sample_log.txt"))


print("\nUNKNOWN NORMALIZED EVENT:")
print(normalize_log(unknown_result, "sample_log.txt"))