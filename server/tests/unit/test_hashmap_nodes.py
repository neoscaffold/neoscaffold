from custom_extensions.core.extension import (
    EXTENSION_MAPPINGS,
    nsHashMap,
    nsHashMapDelete,
    nsHashMapGet,
    nsHashMapHasKey,
    nsHashMapInsert,
    nsHashMapKeys,
    nsHashMapLength,
    nsHashMapMerge,
    nsHashMapValues,
)


def required_inputs(**values):
    return {
        "required_inputs": {
            key: {"values": value}
            for key, value in values.items()
        }
    }


def test_hashmap_node_accepts_json_object_string():
    node = nsHashMap()

    result = node.evaluate({
        "optional_inputs": {
            "initial_data": {"values": '{"name": "neo"}'}
        }
    })

    assert result == {"name": "neo"}


def test_hashmap_insert_returns_updated_copy():
    original = {"a": 1}

    result = nsHashMapInsert().evaluate(
        required_inputs(hashmap=original, key="b", value=2)
    )

    assert result == {"a": 1, "b": 2}
    assert original == {"a": 1}


def test_hashmap_delete_removes_key_without_mutating_input():
    original = {"a": 1, "b": 2}

    result = nsHashMapDelete().evaluate(
        required_inputs(hashmap=original, key="a")
    )

    assert result == {"b": 2}
    assert original == {"a": 1, "b": 2}


def test_hashmap_length_get_and_has_key():
    hashmap = {"a": 1, "b": 2}

    assert nsHashMapLength().evaluate(required_inputs(hashmap=hashmap)) == 2
    assert nsHashMapGet().evaluate(required_inputs(hashmap=hashmap, key="a")) == 1
    assert nsHashMapGet().evaluate({
        "required_inputs": {
            "hashmap": {"values": hashmap},
            "key": {"values": "missing"},
        },
        "optional_inputs": {
            "default": {"values": "fallback"},
        },
    }) == "fallback"
    assert nsHashMapHasKey().evaluate(required_inputs(hashmap=hashmap, key="b")) is True
    assert nsHashMapHasKey().evaluate(required_inputs(hashmap=hashmap, key="c")) is False


def test_hashmap_keys_values_and_merge():
    hashmap = {"a": 1}

    assert nsHashMapKeys().evaluate(required_inputs(hashmap=hashmap)) == ["a"]
    assert nsHashMapValues().evaluate(required_inputs(hashmap=hashmap)) == [1]
    assert nsHashMapMerge().evaluate(
        required_inputs(hashmap=hashmap, updates={"b": 2})
    ) == {"a": 1, "b": 2}
    assert hashmap == {"a": 1}


def test_hashmap_operations_are_registered():
    nodes = EXTENSION_MAPPINGS["nodes"]

    for node_name in [
        "nsHashMapInsert",
        "nsHashMapDelete",
        "nsHashMapLength",
        "nsHashMapGet",
        "nsHashMapHasKey",
        "nsHashMapKeys",
        "nsHashMapValues",
        "nsHashMapMerge",
    ]:
        assert node_name in nodes
