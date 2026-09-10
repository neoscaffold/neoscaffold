from ..extension import MemoryWrite, MemoryRead


def _inputs(key, value=None):
    """Build a node_inputs payload matching the executor's shape."""
    required = {"key": {"values": key}}
    if value is not None:
        required["value"] = {"values": value}
    return {"required_inputs": required}


##########################
# TEST class MemoryWrite:
##########################
def test_memory_write():
    # The executor injects a shared per-execution `_memory` store onto each
    # node instance; mirror that here.
    memory = {}
    memory_write = MemoryWrite()
    memory_write._memory = memory

    result = memory_write.evaluate(_inputs("test_key", "test_value"))

    # The write node echoes the key/value it stored...
    assert result == {"key": "test_key", "value": "test_value"}
    # ...and persists it into the shared memory store.
    assert memory == {"test_key": "test_value"}


##########################
# TEST class MemoryRead:
##########################
def test_memory_read():
    # A prior write in the same execution populated the shared store.
    memory = {"test_key": "test_value"}
    memory_read = MemoryRead()
    memory_read._memory = memory

    result = memory_read.evaluate(_inputs("test_key"))

    # The read node returns the stored value for the given key.
    assert result == "test_value"


def test_memory_read_missing_key_returns_none():
    memory_read = MemoryRead()
    memory_read._memory = {}

    # Missing key short-circuits without touching the store.
    assert memory_read.evaluate({"required_inputs": {}}) is None


def test_memory_write_then_read_share_store():
    # MemoryWrite and MemoryRead cooperate through the same shared store.
    memory = {}
    writer = MemoryWrite()
    reader = MemoryRead()
    writer._memory = memory
    reader._memory = memory

    writer.evaluate(_inputs("greeting", "hello"))

    assert reader.evaluate(_inputs("greeting")) == "hello"
