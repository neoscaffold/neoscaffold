import time
import uuid


def generate_id():
    """Generate a unique ID based on the current time and a random UUID."""
    ms_since_epoch = int(time.time() * 1000)
    return f"{ms_since_epoch}{uuid.uuid4()}"
