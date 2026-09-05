import uuid


def normalize_log(result, filename):
    """
    Convert a processed log into one universal/common schema.

    Input:
        result   -> one processed log from Member 1's parser
        filename -> uploaded source filename
    """

    fields = result.get("fields", {})
    format_type = result.get("format")
    raw_log = result.get("raw")
    confidence = result.get("confidence")

    # Default universal values
    timestamp = None
    event_type = None
    severity = None
    user = None
    message = None

    # =========================================================
    # JSON NORMALIZATION
    # =========================================================

    if format_type == "json" and isinstance(fields, dict):

        timestamp = (
            fields.get("timestamp")
            or fields.get("time")
            or fields.get("event_time")
        )

        event_type = (
            fields.get("event")
            or fields.get("event_type")
            or fields.get("action")
        )

        severity = (
            fields.get("severity")
            or fields.get("level")
        )

        user = (
            fields.get("user")
            or fields.get("username")
        )

        message = (
            fields.get("message")
            or fields.get("msg")
        )

    # =========================================================
    # TEXT / SYSLOG NORMALIZATION
    # =========================================================

    elif format_type == "text" and isinstance(fields, dict):

        timestamp = fields.get("timestamp")
        severity = fields.get("level")
        message = fields.get("message")

        event_type = "system_event"

    # =========================================================
    # CSV NORMALIZATION
    # =========================================================

    elif format_type == "csv" and isinstance(fields, list):

        # Expected example:
        # ["alice", "login", "2026-09-03"]

        if len(fields) > 0:
            user = fields[0]

        if len(fields) > 1:
            event_type = fields[1]

        if len(fields) > 2:
            timestamp = fields[2]

    # =========================================================
    # UNKNOWN / DRAIN3 NORMALIZATION
    # =========================================================

    elif format_type == "unknown_pattern":

        if isinstance(fields, dict):
            message = fields.get("template")

        event_type = "unknown_event"

    # =========================================================
    # RETURN UNIVERSAL EVENT
    # =========================================================

    normalized_event = {
        "event_id": "EVT-" + str(uuid.uuid4()),

        "source_filename": filename,

        "timestamp": timestamp,

        "event_type": event_type,

        "severity": severity,

        "user": user,

        "source_format": format_type,

        "message": message,

        # Preserve original parsed fields
        "parsed_fields": fields,

        # Preserve complete original event
        "raw_event": raw_log,

        "confidence": confidence
    }

    return normalized_event