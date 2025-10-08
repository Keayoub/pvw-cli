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
        
        # Get account ID from environment (optional)
        account_id = os.getenv("PURVIEW_ACCOUNT_ID")

        # Create config
        config = SyncPurviewConfig(
            account_name=account_name, 
            azure_region=os.getenv("AZURE_REGION", "public"),
            account_id=account_id
        )

        # Create synchronous client
        client = SyncPurviewClient(config)

        # Make the request
        # If debug enabled via PURVIEWCLI_DEBUG env var, print helpful diagnostics
        debug = os.getenv("PURVIEWCLI_DEBUG")
        if debug:
            try:
                base_info = {
                    "app": http_dict.get("app"),
                    "method": http_dict.get("method", "GET"),
                    "endpoint": http_dict.get("endpoint", "/"),
                    "params": http_dict.get("params"),
                    "payload": http_dict.get("payload"),
                }
                print("[PURVIEWCLI DEBUG] Request:", json.dumps(base_info, default=str, indent=2))
            except Exception:
                print("[PURVIEWCLI DEBUG] Request: (could not serialize request info)")

        result = client.make_request(
            method=http_dict.get("method", "GET"),
            endpoint=http_dict.get("endpoint", "/"),
            params=http_dict.get("params"),
            json=http_dict.get("payload"),
        )

        if debug:
            try:
                print("[PURVIEWCLI DEBUG] Response:", json.dumps(result, default=str, indent=2))
            except Exception:
                print("[PURVIEWCLI DEBUG] Response: (could not serialize response)")

        # The synchronous client returns a wrapper dict like
        # {"status": "success", "data": <json>, "status_code": 200}
        # Normalize to return the raw JSON payload when available so
        # calling code (which expects the API JSON) works consistently
        if isinstance(result, dict) and result.get("status") == "success" and "data" in result:
            return result.get("data")

        return result

    except Exception as e:
        return {"status": "error", "message": f"Error in real mode: {str(e)}", "data": None}


def get_json(args, param):
    response = None
    # Fix: Use .get() to avoid KeyError if param is missing
    value = args.get(param, None)
    if value is not None:
        import json
        try:
            if isinstance(value, str):
                with open(value, 'r', encoding='utf-8') as f:
                    response = json.load(f)
            else:
                response = value
        except Exception:
            response = None
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
