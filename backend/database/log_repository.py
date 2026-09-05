import json
import uuid

from database.db import get_connection


# ============================================================
# STORE ONE ORIGINAL PROCESSED LOG
# ============================================================

def insert_processed_log(result, filename):
    """
    Store one processed log record in the SQLite database.
    """

    log_id = "LOG-" + str(uuid.uuid4())

    parsed_fields_json = json.dumps(result["fields"])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO processed_logs (
            log_id,
            filename,
            detected_format,
            parsed_fields,
            raw_log,
            confidence
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            log_id,
            filename,
            result["format"],
            parsed_fields_json,
            result["raw"],
            result["confidence"]
        )
    )

    conn.commit()
    conn.close()

    return log_id


# ============================================================
# GET ALL ORIGINAL PROCESSED LOGS
# ============================================================

def get_all_logs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM processed_logs
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================================================
# GET ONE PROCESSED LOG BY LOG ID
# ============================================================

def get_log_by_id(log_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM processed_logs
        WHERE log_id = ?
        """,
        (log_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)

    return None


# ============================================================
# STORE ALL PROCESSED LOGS FROM ONE UPLOAD
# ============================================================

def store_upload_results(filename, results):

    stored_log_ids = []

    for result in results:

        log_id = insert_processed_log(
            result,
            filename
        )

        stored_log_ids.append(log_id)

    return stored_log_ids


# ============================================================
# STORE ONE NORMALIZED EVENT
# ============================================================

def insert_normalized_event(event):
    """
    Store one universal normalized event in SQLite.
    """

    parsed_fields_json = json.dumps(
        event["parsed_fields"]
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO normalized_events (
            event_id,
            source_filename,
            timestamp,
            event_type,
            severity,
            user,
            source_format,
            message,
            parsed_fields,
            raw_event,
            confidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event["event_id"],
            event["source_filename"],
            event["timestamp"],
            event["event_type"],
            event["severity"],
            event["user"],
            event["source_format"],
            event["message"],
            parsed_fields_json,
            event["raw_event"],
            event["confidence"]
        )
    )

    conn.commit()
    conn.close()

    return event["event_id"]


# ============================================================
# STORE ALL NORMALIZED EVENTS
# ============================================================

def store_normalized_events(events):

    stored_event_ids = []

    for event in events:

        event_id = insert_normalized_event(
            event
        )

        stored_event_ids.append(event_id)

    return stored_event_ids


# ============================================================
# GET ALL NORMALIZED EVENTS
# ============================================================

def get_all_normalized_events():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM normalized_events
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================================================
# GET ONE NORMALIZED EVENT BY EVENT ID
# ============================================================

def get_normalized_event_by_id(event_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM normalized_events
        WHERE event_id = ?
        """,
        (event_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)

    return None


# ============================================================
# FILTER + SEARCH + DATE RANGE + PAGINATION
# ============================================================

def filter_normalized_events(
    severity=None,
    event_type=None,
    source_format=None,
    confidence=None,
    user=None,
    search=None,
    start_date=None,
    end_date=None,
    page=1,
    limit=10
):
    """
    Filter normalized events with optional filters,
    search, date range filtering, and pagination.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Base query
    query = """
        SELECT *
        FROM normalized_events
        WHERE 1 = 1
    """

    parameters = []

    # --------------------------------------------------------
    # FILTER BY SEVERITY
    # --------------------------------------------------------

    if severity:
        query += " AND severity = ?"
        parameters.append(severity)

    # --------------------------------------------------------
    # FILTER BY EVENT TYPE
    # --------------------------------------------------------

    if event_type:
        query += " AND event_type = ?"
        parameters.append(event_type)

    # --------------------------------------------------------
    # FILTER BY SOURCE FORMAT
    # --------------------------------------------------------

    if source_format:
        query += " AND source_format = ?"
        parameters.append(source_format)

    # --------------------------------------------------------
    # FILTER BY CONFIDENCE
    # --------------------------------------------------------

    if confidence:
        query += " AND confidence = ?"
        parameters.append(confidence)

    # --------------------------------------------------------
    # FILTER BY USER
    # --------------------------------------------------------

    if user:
        query += " AND user = ?"
        parameters.append(user)

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:

        query += """
            AND (
                message LIKE ?
                OR raw_event LIKE ?
                OR event_type LIKE ?
                OR user LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # --------------------------------------------------------
    # DATE RANGE FILTER
    # --------------------------------------------------------

    if start_date:
        query += " AND timestamp >= ?"
        parameters.append(start_date)

    if end_date:
        query += " AND timestamp <= ?"
        parameters.append(end_date)

    # ========================================================
    # COUNT TOTAL EVENTS BEFORE PAGINATION
    # ========================================================

    count_query = query.replace(
        "SELECT *",
        "SELECT COUNT(*)"
    )

    cursor.execute(
        count_query,
        parameters
    )

    total_events = cursor.fetchone()[0]

    # ========================================================
    # PAGINATION
    # ========================================================

    offset = (page - 1) * limit

    query += """
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """

    parameters.extend([
        limit,
        offset
    ])

    cursor.execute(
        query,
        parameters
    )

    rows = cursor.fetchall()

    conn.close()

    # ========================================================
    # RESPONSE
    # ========================================================

    return {
        "total_events": total_events,
        "page": page,
        "limit": limit,
        "total_pages": (
            (total_events + limit - 1) // limit
            if total_events > 0
            else 0
        ),
        "events": [
            dict(row)
            for row in rows
        ]
    }