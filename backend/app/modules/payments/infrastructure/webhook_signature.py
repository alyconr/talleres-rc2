import hashlib
import hmac
import time


def verify_webhook_signature(
    *,
    signature_header: str | None,
    request_id: str | None,
    data_id: str | None,
    secret: str,
    now: float | None = None,
    tolerance_seconds: int = 300,
) -> bool:
    if not signature_header or not request_id or not data_id or not secret:
        return False

    fields: dict[str, str] = {}
    for part in signature_header.split(","):
        key, separator, value = part.strip().partition("=")
        if not separator or key in fields:
            return False
        fields[key] = value

    timestamp = fields.get("ts")
    received_hash = fields.get("v1")
    if not timestamp or not received_hash:
        return False
    try:
        timestamp_value = int(timestamp)
    except ValueError:
        return False

    timestamp_seconds = timestamp_value / 1000 if timestamp_value > 10**12 else timestamp_value
    current_time = time.time() if now is None else now
    if abs(current_time - timestamp_seconds) > tolerance_seconds:
        return False

    manifest = f"id:{data_id};request-id:{request_id};ts:{timestamp};"
    expected_hash = hmac.new(
        secret.encode(), manifest.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_hash, received_hash)
