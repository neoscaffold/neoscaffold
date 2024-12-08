from ..extension import MemoryWrite, MemoryRead
##########################
# TEST class MemoryWrite:
##########################
def test_memory_write():
    # Create an instance of MemoryWrite
    memory_write = MemoryWrite()

    # Define test inputs
    test_inputs = {
        "required_inputs": {
            "key": {"values": "test_key"},
            "value": {"values": "test_value"}
        }
    }

    # Call the evaluate method with the test inputs
    result = memory_write.evaluate(test_inputs)

    # Check if the result is as expected
    expected_output = {"test_key": "test_value"}
    assert result == expected_output, f"Expected {expected_output}, but got {result}"

    print("MemoryWrite test passed! ......")

# Run the test
# test_memory_write()
# ##########################

def test_memory_read():
    # Create an instance of MemoryWrite
    memory_read = MemoryRead()

    # Define test inputs
    test_inputs = {
        "required_inputs": {
            "key": {"values": "test_key"},
            "value": {"values": "test_value"}
        }
    }

    # Call the evaluate method with the test inputs
    result = memory_read.evaluate(test_inputs)

    # Check if the result is as expected
    expected_output = {"test_key": "test_value"}
    assert result == expected_output, f"Expected {expected_output}, but got {result}"

    print("MemoryRead test passed! ......")