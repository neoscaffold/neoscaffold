import requests
import json
import time

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

version = "0.0.1"


def fetch_handle(response, response_type, fetch_handle_parameters):
    asset_id = fetch_handle_parameters.get("id")
    status = response.status_code

    try:
        if response_type == "json":
            resp_json = response.json()
            return status, resp_json
        elif response_type == "binary_file":
            with open(asset_id, "wb") as f:
                f.write(response.content)
            return status, asset_id
        else:
            text = response.text
            return status, text
    except ValueError:
        raise Exception(
            f"Error parsing response as {response_type}. HTTP status code: {status}"
        )
    except IOError:
        raise Exception(f"Error writing to file {asset_id}. HTTP status code: {status}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}. HTTP status code: {status}")


def fetch(
    url,
    method="GET",
    payload=None,
    headers=None,
    response_type="json",
    fetch_handle_parameters={},
):
    """fetch a single request with retries and exponential backoff"""
    retry_count = 0
    while retry_count < 5:
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=payload, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=payload, headers=headers)
            elif method == "PATCH":
                response = requests.patch(url, json=payload, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError("Invalid method")
            return fetch_handle(response, response_type, fetch_handle_parameters)
        except Exception as e:
            print(e)
            retry_count += 1
            time.sleep(2**retry_count)
    return None


def process_batch(batch, response_type="json"):
    """process a batch of requests"""

    num_workers = 5 * cpu_count()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for request in batch:
            future = executor.submit(
                fetch,
                request.get("url"),
                request.get("method"),
                request.get("payload"),
                request.get("headers"),
                response_type,
                fetch_handle_parameters=request.get("fetch_handle_parameters", {}),
            )
            futures.append(future)
        request_responses = [future.result() for future in futures]
    return [
        {"request": batch[i], "response": {"status": r[0], "body": r[1]}}
        for i, r in enumerate(request_responses)
    ]


def request_generator(batches, response_type):
    """Generator function that yields batches of requests"""
    for i, batch in enumerate(batches):
        print(f"batch_num: {i}")
        yield process_batch(batch, response_type)


class POSTJSONNetworkRequest:
    # LABELS
    CATEGORY = "networking"
    SUBCATEGORY = "POST"
    DESCRIPTION = "Make a POST request"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "uri": {
                "kind": "*",
                "name": "uri",
                "widget": {"kind": "string", "name": "uri", "default": ""},
            },
            "body": {
                "kind": "*",
                "name": "body",
                "widget": {"kind": "string", "name": "body", "default": "{}"},
            },
            "headers": {
                "kind": "*",
                "name": "headers",
                "widget": {"kind": "string", "name": "headers", "default": "{}"},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "RESPONSE",
        "name": "RESPONSE",
        "cacheable": True,
    }

    # METHODS
    def evaluate(self, node_inputs):
        uri = node_inputs.get("required_inputs").get("uri").get("values")
        body = node_inputs.get("required_inputs").get("body").get("values")
        headers = node_inputs.get("required_inputs").get("headers").get("values")

        print(f"uri: {uri}")
        print(f"body: {body}")
        print(f"headers: {body}")

        batches = [
            [
                {
                    "url": uri,
                    "method": "POST",
                    "headers": json.loads(headers),
                    "payload": json.loads(body),
                }
            ]
        ]

        print(json.dumps(batches))
        responses = json.dumps(
            list(request_generator(batches=batches, response_type="json"))[0][0]
        )

        return responses


class GETJSONNetworkRequest:
    # LABELS
    CATEGORY = "networking"
    SUBCATEGORY = "GET"
    DESCRIPTION = "Make a GET request"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "uri": {
                "kind": "*",
                "name": "uri",
                "widget": {"kind": "string", "name": "uri", "default": ""},
            },
            "headers": {
                "kind": "*",
                "name": "headers",
                "widget": {"kind": "string", "name": "headers", "default": "{}"},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "RESPONSE",
        "name": "RESPONSE",
        "cacheable": True,
    }

    # METHODS
    def evaluate(self, node_inputs):
        uri = node_inputs.get("required_inputs").get("uri").get("values")
        headers = node_inputs.get("required_inputs").get("headers").get("values")

        print(f"uri: {uri}")
        print(f"headers: {headers}")

        batches = [
            [
                {
                    "url": uri,
                    "method": "GET",
                    "headers": json.loads(headers),
                }
            ]
        ]

        print(json.dumps(batches))
        responses = json.dumps(
            list(request_generator(batches=batches, response_type="json"))[0][0]
        )

        return responses


class PUTJSONNetworkRequest:
    # LABELS
    CATEGORY = "networking"
    SUBCATEGORY = "PUT"
    DESCRIPTION = "Make a PUT request"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "uri": {
                "kind": "*",
                "name": "uri",
                "widget": {"kind": "string", "name": "uri", "default": ""},
            },
            "body": {
                "kind": "*",
                "name": "body",
                "widget": {"kind": "string", "name": "body", "default": "{}"},
            },
            "headers": {
                "kind": "*",
                "name": "headers",
                "widget": {"kind": "string", "name": "headers", "default": "{}"},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "RESPONSE",
        "name": "RESPONSE",
        "cacheable": True,
    }

    # METHODS
    def evaluate(self, node_inputs):
        uri = node_inputs.get("required_inputs").get("uri").get("values")
        body = node_inputs.get("required_inputs").get("body").get("values")
        headers = node_inputs.get("required_inputs").get("headers").get("values")

        print(f"uri: {uri}")
        print(f"body: {body}")
        print(f"headers: {headers}")

        batches = [
            [
                {
                    "url": uri,
                    "method": "PUT",
                    "headers": json.loads(headers),
                    "payload": json.loads(body),
                }
            ]
        ]

        print(json.dumps(batches))
        responses = json.dumps(
            list(request_generator(batches=batches, response_type="json"))[0][0]
        )

        return responses


class PATCHJSONNetworkRequest:
    # LABELS
    CATEGORY = "networking"
    SUBCATEGORY = "PATCH"
    DESCRIPTION = "Make a PATCH request"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "uri": {
                "kind": "*",
                "name": "uri",
                "widget": {"kind": "string", "name": "uri", "default": ""},
            },
            "body": {
                "kind": "*",
                "name": "body",
                "widget": {"kind": "string", "name": "body", "default": "{}"},
            },
            "headers": {
                "kind": "*",
                "name": "headers",
                "widget": {"kind": "string", "name": "headers", "default": "{}"},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "RESPONSE",
        "name": "RESPONSE",
        "cacheable": True,
    }

    # METHODS
    def evaluate(self, node_inputs):
        uri = node_inputs.get("required_inputs").get("uri").get("values")
        body = node_inputs.get("required_inputs").get("body").get("values")
        headers = node_inputs.get("required_inputs").get("headers").get("values")

        print(f"uri: {uri}")
        print(f"body: {body}")
        print(f"headers: {headers}")

        batches = [
            [
                {
                    "url": uri,
                    "method": "PATCH",
                    "headers": json.loads(headers),
                    "payload": json.loads(body),
                }
            ]
        ]

        print(json.dumps(batches))
        responses = json.dumps(
            list(request_generator(batches=batches, response_type="json"))[0][0]
        )

        return responses


class DELETEJSONNetworkRequest:
    # LABELS
    CATEGORY = "networking"
    SUBCATEGORY = "DELETE"
    DESCRIPTION = "Make a DELETE request"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "body": {
                "kind": "*",
                "name": "body",
                "widget": {"kind": "string", "name": "body", "default": "{}"},
            },
            "headers": {
                "kind": "*",
                "name": "headers",
                "widget": {"kind": "string", "name": "headers", "default": "{}"},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "RESPONSE",
        "name": "RESPONSE",
        "cacheable": True,
    }

    # METHODS
    def evaluate(self, node_inputs):
        uri = node_inputs.get("required_inputs").get("uri").get("values")
        headers = node_inputs.get("required_inputs").get("headers").get("values")

        print(f"uri: {uri}")
        print(f"headers: {headers}")

        batches = [[{"url": uri, "method": "DELETE", "headers": json.loads(headers)}]]

        print(json.dumps(batches))
        responses = json.dumps(
            list(request_generator(batches=batches, response_type="json"))[0][0]
        )

        return responses


class ConsoleLog:
    CATEGORY = "utilities"
    SUBCATEGORY = "logging"
    DESCRIPTION = "Make a request to the TGI API"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "any": {
                "kind": "*",
                "name": "any",
                "widget": {"kind": "string", "name": "any", "default": ""},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "any",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        output_value = ""
        if node_inputs.get("required_inputs"):
            if "any" in node_inputs.get("required_inputs"):
                self.any = node_inputs.get("required_inputs").get("any").get("values")
                output_value = self.any
                print(output_value)

        return output_value


# RULES
class TextLength:
    CATEGORY = "unstructured_text"
    SUBCATEGORY = "metrics"
    DESCRIPTION = "Check the length of text"

    PARAMETERS = {
        # "severity" is a default optional parameter available to all rules of type "int" 1-5
        "required_parameters": {
            # magic parameter formed by the list representing the value_path: ["datasource", "input", "required_inputs", "body", "values"] that resolves "source_input" to a value from the data source
            "value_path": {
                # type of the value AT the value_path
                "kind": "str",
                "name": "value_path",
                "widget": {"kind": "string", "name": "value_path", "default": ""},
            }
        },
        "optional_parameters": {
            "min_length": {
                "kind": "int",
                "name": "min_length",
                "widget": {"kind": "number", "name": "min_length", "default": 0},
            },
            "max_length": {
                "kind": "int",
                "name": "max_length",
                "widget": {"kind": "number", "name": "max_length", "default": 0},
            },
        },
    }

    def evaluate(self, source_input, parameters):
        str_length = len(source_input)

        outcome = {"passed": True, "causes": {}}

        max_length = (
            parameters.get("optional_parameters", {})
            .get("max_length", {})
            .get("values")
        )
        min_length = (
            parameters.get("optional_parameters", {})
            .get("min_length", {})
            .get("values")
        )

        if max_length is None and min_length is None:
            raise ValueError(
                "Rule: TextLength - Parameter Error: Must provide a max or min value"
            )

        if max_length is not None and str_length > max_length:
            outcome["passed"] = False
            outcome["causes"]["max_length"] = {
                "message": f"String length of {str_length} is greater than {max_length}",
                "outliers": {
                    "str_length": str_length,
                },
            }

        if min_length is not None and str_length < min_length:
            outcome["passed"] = False
            outcome["causes"]["min_length"] = {
                "message": f"String length of {str_length} is less than {min_length}",
                "outliers": {
                    "str_length": str_length,
                },
            }

        return outcome


# Hook Functions


def before_load():
    print("before requests load")


def on_load():
    print("requests load")


def after_load():
    print("after requests load")


def before_enable():
    print("before requests enable")


def on_enable():
    print("requests enabled")


def after_enable():
    print("after requests enable")


def before_disable():
    print("before requests disable")


def on_disable():
    print("requests disabled")


def after_disable():
    print("after requests disable")


def before_install():
    print("before requests install")


def on_install():
    print("requests installed")


def after_install():
    print("After requests installed")


def before_uninstall():
    print("Before requests uninstall")


def on_uninstall():
    print("requests uninstalled")


def after_uninstall():
    print("After requests uninstalled")


EXTENSION_MAPPINGS = {
    "name": "requests",
    "version": version,
    "description": "Extension for making requests",
    "javascript_class_name": "requests",
    "nodes": {
        "POSTJSONNetworkRequest": {
            "python_class": POSTJSONNetworkRequest,
            "javascript_class_name": "POSTJSONNetworkRequest",
            "display_name": "POSTRequest",
        },
        "GETJSONNetworkRequest": {
            "python_class": GETJSONNetworkRequest,
            "javascript_class_name": "GETJSONNetworkRequest",
            "display_name": "GETRequest",
        },
        "PUTJSONNetworkRequest": {
            "python_class": PUTJSONNetworkRequest,
            "javascript_class_name": "PUTJSONNetworkRequest",
            "display_name": "PUTRequest",
        },
        "PATCHJSONNetworkRequest": {
            "python_class": PATCHJSONNetworkRequest,
            "javascript_class_name": "PATCHJSONNetworkRequest",
            "display_name": "PATCHRequest",
        },
        "DELETEJSONNetworkRequest": {
            "python_class": DELETEJSONNetworkRequest,
            "javascript_class_name": "DELETEJSONNetworkRequest",
            "display_name": "DELETERequest",
        },
        "ConsoleLog": {
            "python_class": ConsoleLog,
            "javascript_class_name": "ConsoleLog",
            "display_name": "Console Log",
        },
    },
    "rules": {
        "TextLength": {
            "python_class": TextLength,
            "javascript_class_name": "TextLength",
            "display_name": "Text Length",
        },
    },
    "hooks": {
        "before_load": before_load,
        "on_load": on_load,
        "after_load": after_load,
        "before_enable": before_enable,
        "on_enable": on_enable,
        "after_enable": after_enable,
        "before_disable": before_disable,
        "on_disable": on_disable,
        "after_disable": after_disable,
        "before_install": before_install,
        "on_install": on_install,
        "after_install": after_install,
        "before_uninstall": before_uninstall,
        "on_uninstall": on_uninstall,
        "after_uninstall": after_uninstall,
    },
}
