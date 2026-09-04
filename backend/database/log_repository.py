import json
import uuid

from database.db import get_connection


def insert_processed_log(result, filename):
    """
    Store one processed log record in the SQLite database.

    Parameters:
        result: Processed log dictionary returned by Member 1
        filename: Name of the uploaded file
    """

    # Generate a unique ID for the processed log
    log_id = "LOG-" + str(uuid.uuid4())

    # Convert dictionary/list fields into JSON text
    parsed_fields_json = json.dumps(result["fields"])

    # Connect to the database
    conn = get_connection()
    cursor = conn.cursor()

    # Insert the processed log
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


def get_all_logs():
    """
    Retrieve all processed logs from the database.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM processed_logs
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]
def get_log_by_id(log_id):
    """
    Retrieve one processed log using its unique log ID.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM processed_logs
        WHERE log_id = ?
        """,
        (log_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)

    return None

def store_upload_results(filename, results):
    """
    Store all processed log results from one uploaded file.

    Parameters:
        filename: Name of the uploaded file
        results: List of processed log dictionaries returned by Member 1
    """

    stored_log_ids = []

    for result in results:

        log_id = insert_processed_log(
            result,
            filename
        )

        stored_log_ids.append(log_id)

    return stored_log_ids