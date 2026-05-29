from custom_extensions.core.extension import (
    EXTENSION_MAPPINGS,
    nsArray,
    nsArrayAppend,
    nsArrayConcat,
    nsArrayContains,
    nsArrayDelete,
    nsArrayGet,
    nsArrayIndexOf,
    nsArrayInsert,
    nsArrayLength,
    nsArraySet,
    nsArraySlice,
)


def required_inputs(**values):
    return {
        "required_inputs": {
            key: {"values": value}
            for key, value in values.items()
        }
    }


def test_array_node_accepts_json_array_string():
    node = nsArray()

    result = node.evaluate({
        "optional_inputs": {
            "initial_data": {"values": "[1, 2, 3]"}
        }
    })

    assert result == [1, 2, 3]


def test_array_append_returns_updated_copy():
    original = [1]

    result = nsArrayAppend().evaluate(
        required_inputs(array=original, element=2)
    )

    assert result == [1, 2]
    assert original == [1]


def test_array_get_length_contains_and_index_of():
    array = ["a", "b", "c"]

    assert nsArrayLength().evaluate(required_inputs(array=array)) == 3
    assert nsArrayGet().evaluate(required_inputs(array=array, index=1)) == "b"
    assert nsArrayGet().evaluate({
        "required_inputs": {
            "array": {"values": array},
            "index": {"values": 99},
        },
        "optional_inputs": {
            "default": {"values": "fallback"},
        },
    }) == "fallback"
    assert nsArrayContains().evaluate(required_inputs(array=array, value="c")) is True
    assert nsArrayContains().evaluate(required_inputs(array=array, value="z")) is False
    assert nsArrayIndexOf().evaluate(required_inputs(array=array, value="b")) == 1
    assert nsArrayIndexOf().evaluate(required_inputs(array=array, value="z")) == -1


def test_array_set_insert_delete_slice_and_concat():
    original = [1, 2, 3]

    assert nsArraySet().evaluate(
        required_inputs(array=original, index=1, value=9)
    ) == [1, 9, 3]
    assert nsArrayInsert().evaluate(
        required_inputs(array=original, index=1, element=8)
    ) == [1, 8, 2, 3]
    assert nsArrayDelete().evaluate(
        required_inputs(array=original, index=1)
    ) == [1, 3]
    assert nsArraySlice().evaluate({
        "required_inputs": {
            "array": {"values": original},
        },
        "optional_inputs": {
            "start": {"values": 1},
            "end": {"values": 3},
        },
    }) == [2, 3]
    assert nsArrayConcat().evaluate(
        required_inputs(array=original, other_array=[4, 5])
    ) == [1, 2, 3, 4, 5]
    assert original == [1, 2, 3]


def test_array_operations_are_registered():
    nodes = EXTENSION_MAPPINGS["nodes"]

    for node_name in [
        "nsArrayGet",
        "nsArraySet",
        "nsArrayInsert",
        "nsArrayDelete",
        "nsArrayContains",
        "nsArrayIndexOf",
        "nsArraySlice",
        "nsArrayConcat",
    ]:
        assert node_name in nodes
