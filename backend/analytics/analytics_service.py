from database.log_repository import get_all_normalized_events


def get_summary_analytics():
    """
    Generate summary analytics from all normalized events.
    """

    # Get all normalized events from database
    events = get_all_normalized_events()

    total_events = len(events)

    # Dictionaries for analytics
    format_counts = {}
    event_type_counts = {}
    severity_counts = {}
    confidence_counts = {}

    # Process every event
    for event in events:

        # ------------------------------------------------
        # COUNT BY SOURCE FORMAT
        # ------------------------------------------------

        source_format = event.get("source_format")

        if source_format:

            format_counts[source_format] = (
                format_counts.get(source_format, 0) + 1
            )


        # ------------------------------------------------
        # COUNT BY EVENT TYPE
        # ------------------------------------------------

        event_type = event.get("event_type")

        if event_type:

            event_type_counts[event_type] = (
                event_type_counts.get(event_type, 0) + 1
            )


        # ------------------------------------------------
        # COUNT BY SEVERITY
        # ------------------------------------------------

        severity = event.get("severity")

        if severity:

            severity_counts[severity] = (
                severity_counts.get(severity, 0) + 1
            )


        # ------------------------------------------------
        # COUNT BY CONFIDENCE
        # ------------------------------------------------

        confidence = event.get("confidence")

        if confidence:

            confidence_counts[confidence] = (
                confidence_counts.get(confidence, 0) + 1
            )


    # ------------------------------------------------
    # RETURN ANALYTICS SUMMARY
    # ------------------------------------------------

    return {

        "total_events": total_events,

        "events_by_format": format_counts,

        "events_by_type": event_type_counts,

        "events_by_severity": severity_counts,

        "events_by_confidence": confidence_counts

    }