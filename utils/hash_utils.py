import hashlib
import json


def hash_sensor_reading(data):
    """
    Generate deterministic SHA256 hash for a sensor reading.
    """

    # Sort keys to ensure consistent hashing
    ordered_data = json.dumps(data, sort_keys=True)

    # Encode to bytes
    encoded_data = ordered_data.encode("utf-8")

    # Generate SHA256
    hash_value = hashlib.sha256(encoded_data).hexdigest()

    return hash_value


def hash_batch_payload(batch_payload):
    """
    Hash entire batch JSON before IPFS upload
    (optional additional integrity layer)
    """

    ordered_data = json.dumps(batch_payload, sort_keys=True)
    encoded_data = ordered_data.encode("utf-8")
    hash_value = hashlib.sha256(encoded_data).hexdigest()

    return hash_value


def to_bytes32(hex_string):
    """
    Convert 64-char hex string to 0x-prefixed bytes32
    Required for blockchain storage
    """

    if not hex_string:
        return None

    # Remove existing 0x if present
    hex_string = hex_string.replace("0x", "")

    if len(hex_string) != 64:
        raise ValueError("Invalid SHA256 hash length for bytes32")

    return "0x" + hex_string