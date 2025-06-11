import sys
import json
import os
from .sync_client import SyncPurviewClient, SyncPurviewConfig


class Endpoint:
    def __init__(self):
        self.app = None
        self.method = None
        self.endpoint = None
        self.params = None
        self.payload = None
        self.files = None
        self.headers = {}


def get_data(http_dict):
    """Execute HTTP request using SyncPurviewClient"""
    try:
        # Get account name from environment or use default
        account_name = os.getenv(
            "PURVIEW_ACCOUNT_NAME", http_dict.get("account_name", "test-purview-account")
        )

        # Create config
        config = SyncPurviewConfig(
            account_name=account_name, azure_region=os.getenv("AZURE_REGION", "public")
        )

        # Create synchronous client
        client = SyncPurviewClient(config)

        # Make the request
        result = client.make_request(
            method=http_dict.get("method", "GET"),
            endpoint=http_dict.get("endpoint", "/"),
            params=http_dict.get("params"),
            json=http_dict.get("payload"),
        )

        return result

    except Exception as e:
        return {"status": "error", "message": f"Error in real mode: {str(e)}", "data": None}


def get_json(args, param):
    response = None
    if args[param] is not None:
        filepath = args[param]
        if ".JSON" in filepath.upper():
            try:
                with open(filepath, encoding="utf-8") as f:
                    response = json.load(f)
            except:
                with open(filepath, encoding="utf-16") as f:
                    response = json.load(f)
        else:
            print(
                "[ERROR] The {0} parameter must contain a valid file path to a JSON document.".format(
                    param
                )
            )
            sys.exit()
    return response


def decorator(func):
    def wrapper(self, args):
        func(self, args)
        http_dict = {
            "app": self.app,
            "method": self.method,
            "endpoint": self.endpoint,
            "params": self.params,
            "payload": self.payload,
            "files": self.files,
            "headers": self.headers,
        }
        data = get_data(http_dict)
        return data

    return wrapper


def no_api_call_decorator(func):
    """Decorator for operations that don't require API calls"""
    def wrapper(self, args):
        func(self, args)
        # Return success status without making HTTP request
        return {"status_code": None, "message": "operation completed", "data": None}

    return wrapper
