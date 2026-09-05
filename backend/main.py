from fastapi import FastAPI, File, UploadFile

import json
import csv
import re

from drain3 import TemplateMiner

# Universal schema normalizer
from processors.normalizer import normalize_log

# Analytics
from analytics.analytics_service import get_summary_analytics

# Database
from database.db import initialize_database

from database.log_repository import (
    store_upload_results,
    get_all_logs,
    get_log_by_id,
    store_normalized_events,
    get_all_normalized_events,
    get_normalized_event_by_id,
    filter_normalized_events
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(title="Universal Log Pre-processor")


# ============================================================
# INITIALIZE SQLITE DATABASE
# ============================================================

initialize_database()


# ============================================================
# ONE SHARED DRAIN3 INSTANCE
# ============================================================

template_miner = TemplateMiner()


# ============================================================
# DETECT LOG FORMAT
# ============================================================

def detect_format(line):

    # 1. JSON
    try:
        json.loads(line)
        return "json"

    except json.JSONDecodeError:
        pass


    # 2. TEXT / SYSLOG
    text_pattern = (
        r"^\d{4}-\d{2}-\d{2} "
        r"\d{2}:\d{2}:\d{2} "
        r"(INFO|ERROR|WARNING|DEBUG) "
        r"(.*)$"
    )

    if re.search(text_pattern, line):
        return "text"


    # 3. CSV
    try:

        row = next(csv.reader([line]))

        if len(row) >= 2 and all(field.strip() for field in row):
            return "csv"

    except csv.Error:
        pass


    # 4. UNKNOWN
    return "unknown"


# ============================================================
# PARSE CSV
# ============================================================

def parse_csv(line):

    return next(csv.reader([line]))


# ============================================================
# PARSE TEXT / SYSLOG
# ============================================================

def parse_text(line):

    pattern = (
        r"(\d{4}-\d{2}-\d{2} "
        r"\d{2}:\d{2}:\d{2}) "
        r"(INFO|ERROR|WARNING|DEBUG) "
        r"(.*)"
    )

    result = re.search(pattern, line)

    if result:

        return {
            "timestamp": result.group(1),
            "level": result.group(2),
            "message": result.group(3)
        }

    return {}


# ============================================================
# PARSE UNKNOWN LOG USING DRAIN3
# ============================================================

def parse_unknown(line):

    result = template_miner.add_log_message(line)

    cluster = template_miner.drain.id_to_cluster[
        result["cluster_id"]
    ]

    return {
        "template": cluster.get_template()
    }


# ============================================================
# POST: UPLOAD AND PROCESS LOG FILE
# ============================================================

@app.post("/upload")
async def upload_log_file(file: UploadFile = File(...)):

    # Read file
    contents = await file.read()


    # Handle invalid UTF-8
    try:

        text_data = contents.decode("utf-8")

    except UnicodeDecodeError:

        return {
            "filename": file.filename,
            "error": "File is not valid UTF-8"
        }


    # Split file into lines
    lines = text_data.splitlines()

    results = []


    # ========================================================
    # PROCESS EACH LOG LINE
    # ========================================================

    for line in lines:

        # Skip blank lines
        if not line.strip():
            continue


        # Detect format
        format_type = detect_format(line)


        # JSON
        if format_type == "json":

            fields = json.loads(line)
            confidence = "high"


        # CSV
        elif format_type == "csv":

            fields = parse_csv(line)
            confidence = "high"


        # TEXT
        elif format_type == "text":

            fields = parse_text(line)
            confidence = "medium"


        # UNKNOWN
        else:

            fields = parse_unknown(line)

            format_type = "unknown_pattern"

            confidence = "low"


        # Store processed result
        results.append({

            "format": format_type,

            "fields": fields,

            "raw": line,

            "confidence": confidence

        })


    # ========================================================
    # UNIVERSAL NORMALIZATION
    # ========================================================

    normalized_results = []

    for result in results:

        normalized_event = normalize_log(
            result,
            file.filename
        )

        normalized_results.append(
            normalized_event
        )


    # ========================================================
    # STORE ORIGINAL LOGS
    # ========================================================

    stored_log_ids = store_upload_results(

        file.filename,

        results

    )


    # ========================================================
    # STORE NORMALIZED EVENTS
    # ========================================================

    stored_event_ids = store_normalized_events(

        normalized_results

    )


    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return {

        "filename": file.filename,

        "results": results,

        "normalized_results": normalized_results,

        "stored_log_ids": stored_log_ids,

        "stored_event_ids": stored_event_ids

    }


# ============================================================
# GET: ANALYTICS SUMMARY
# ============================================================

@app.get("/analytics/summary")
def analytics_summary():

    return get_summary_analytics()


# ============================================================
# GET: ALL ORIGINAL PROCESSED LOGS
# ============================================================

@app.get("/logs")
def get_logs():

    logs = get_all_logs()

    return {

        "total_logs": len(logs),

        "logs": logs

    }


# ============================================================
# GET: ONE ORIGINAL LOG
# ============================================================

@app.get("/logs/{log_id}")
def get_single_log(log_id: str):

    log = get_log_by_id(log_id)

    if log is None:

        return {
            "message": "Log not found"
        }

    return log


# ============================================================
# GET: ALL NORMALIZED EVENTS
# ============================================================

@app.get("/normalized-events")
def get_normalized_events():

    events = get_all_normalized_events()

    return {

        "total_events": len(events),

        "events": events

    }

# ============================================================
# GET: FILTER NORMALIZED EVENTS
# ============================================================

@app.get("/normalized-events/filter/")
def filter_events(
    severity: str = None,
    event_type: str = None,
    source_format: str = None,
    confidence: str = None,
    user: str = None
):
    events = filter_normalized_events(
        severity=severity,
        event_type=event_type,
        source_format=source_format,
        confidence=confidence,
        user=user
    )

    return {
        "total_events": len(events),
        "filters": {
            "severity": severity,
            "event_type": event_type,
            "source_format": source_format,
            "confidence": confidence,
            "user": user
        },
        "events": events
    }
# ============================================================
# GET: FILTER + SEARCH + DATE RANGE + PAGINATION
# ============================================================

@app.get("/normalized-events/filter")
def filter_events(
    severity: str = None,
    event_type: str = None,
    source_format: str = None,
    confidence: str = None,
    user: str = None,
    search: str = None,
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    limit: int = 10
):
    return filter_normalized_events(
        severity=severity,
        event_type=event_type,
        source_format=source_format,
        confidence=confidence,
        user=user,
        search=search,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )

# ============================================================
# GET: ONE NORMALIZED EVENT
# ============================================================

@app.get("/normalized-events/{event_id}")
def get_single_normalized_event(event_id: str):

    event = get_normalized_event_by_id(event_id)

    if event is None:

        return {
            "message": "Normalized event not found"
        }

    return event