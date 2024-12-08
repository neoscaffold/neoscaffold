import requests
import json
import os
import time

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count


def write_failures(failures_dict, path):
    if len(failures_dict):
        data = {}
        if os.path.exists(path):
            with open(path, "r") as fg:
                data = json.load(fg)
                data.update(failures_dict)
        with open(path, "w+") as fg:
            fg.write(json.dumps(data, indent=4))
            fg.close()


def fetch_handle(response, response_type, fetch_handle_parameters):
    asset_id = fetch_handle_parameters.get("id")
    if response_type == "json":
        resp_json = response.json()
        status = response.status_code
        return status, resp_json
    if response_type == "binary_file":
        with open(asset_id, "wb") as f:
            f.write(response.content)
        status = response.status_code
        return status, asset_id
    else:
        text = response.text
        status = response.status_code
        return status, text


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
        {"request": batch[i], "response": r} for i, r in enumerate(request_responses)
    ]


def request_generator(batches, response_type, failure_path=None):
    """Generator function that yields batches of requests"""
    ids_that_failed = {}

    for i, batch in enumerate(batches):
        print(f"batch_num: {i}")
        if failure_path:
            write_failures(ids_that_failed, failure_path)
        yield process_batch(batch, response_type)
