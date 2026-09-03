from fastapi import FastAPI, File, UploadFile
import json
import csv
import re
from drain3 import TemplateMiner

app = FastAPI(title="Universal Log Pre-processor")

# One shared Drain3 instance
template_miner = TemplateMiner()


def detect_format(line):
    # 1. JSON
    try:
        json.loads(line)
        return "json"
    except json.JSONDecodeError:
        pass

    # 2. Text / Syslog
    text_pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (INFO|ERROR|WARNING|DEBUG) (.*)$"

    if re.search(text_pattern, line):
        return "text"

    # 3. CSV
    try:
        row = next(csv.reader([line]))

        if len(row) >= 2 and all(field.strip() for field in row):
            return "csv"
    except csv.Error:
        pass

    # 4. Unknown
    return "unknown"


def parse_csv(line):
    return next(csv.reader([line]))


def parse_text(line):
    pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (INFO|ERROR|WARNING|DEBUG) (.*)"

    result = re.search(pattern, line)

    if result:
        return {
            "timestamp": result.group(1),
            "level": result.group(2),
            "message": result.group(3)
        }

    return {}


def parse_unknown(line):
    result = template_miner.add_log_message(line)

    cluster = template_miner.drain.id_to_cluster[result["cluster_id"]]

    return {
        "template": cluster.get_template()
    }


@app.post("/upload")
async def upload_log_file(file: UploadFile = File(...)):
    contents = await file.read()

    # Handle invalid UTF-8
    try:
        text_data = contents.decode("utf-8")
    except UnicodeDecodeError:
        return {
            "filename": file.filename,
            "error": "File is not valid UTF-8"
        }

    lines = text_data.splitlines()

    results = []

    for line in lines:

        # Skip blank lines
        if not line.strip():
            continue

        format_type = detect_format(line)

        if format_type == "json":
            fields = json.loads(line)
            confidence = "high"

        elif format_type == "csv":
            fields = parse_csv(line)
            confidence = "high"

        elif format_type == "text":
            fields = parse_text(line)
            confidence = "medium"

        else:
            fields = parse_unknown(line)
            format_type = "unknown_pattern"
            confidence = "low"

        results.append({
            "format": format_type,
            "fields": fields,
            "raw": line,
            "confidence": confidence
        })

    return {
        "filename": file.filename,
        "results": results
    }