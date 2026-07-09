# SPDX-License-Identifier: Apache-2.0

"""
Microsoft Purview Data Quality API Client
Data Quality operations for Unified Catalog quality namespace.
"""

from .endpoint import Endpoint, decorator, get_json
from .endpoints import ENDPOINTS, format_endpoint, get_api_version_params


class DataQuality(Endpoint):
    """Client for Microsoft Purview Data Quality API."""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "datagovernance"

    def _reset_request_state(self):
        # Cached clients are reused between commands, so clear mutable request state.
        self.payload = None
        self.files = None
        self.headers = {}

    def _first(self, args, key, default=""):
        value = args.get(key, default)
        if isinstance(value, list):
            return value[0] if value else default
        return value

    def _int_param(self, args, key):
        value = self._first(args, key, None)
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _float_param(self, args, key):
        value = self._first(args, key, None)
        if value in (None, ""):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _list_param(self, args, key):
        value = args.get(key)
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return None

    def _base_params(self, args):
        params = get_api_version_params("quality")
        filter_value = self._first(args, "--filter", "")
        if filter_value:
            params["filter"] = filter_value

        skip = self._int_param(args, "--skip")
        top = self._int_param(args, "--top")
        if skip is not None:
            params["skip"] = skip
        if top is not None:
            params["top"] = top
        return params

    def _body_from_args(self, args, optional_fields=None):
        payload = get_json(args, "--payloadFile")
        if payload:
            return payload

        body = args.get("body")
        if body:
            return body

        body = {}
        optional_fields = optional_fields or {}
        for cli_key, payload_key in optional_fields.items():
            value = self._first(args, cli_key, "")
            if value != "":
                body[payload_key] = value
        return body if body else None

    # Domain report
    @decorator
    def list_business_domains(self, args):
        self._reset_request_state()
        self.method = "GET"
        self.endpoint = ENDPOINTS["data_quality"]["list_business_domains"]
        self.params = self._base_params(args)

    @decorator
    def get_domain_report(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["get_domain_report"], domainId=domain_id
        )
        self.params = self._base_params(args)

    @decorator
    def list_domain_data_sources(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["list_domain_data_sources"], domainId=domain_id
        )
        self.params = self._base_params(args)

    @decorator
    def list_domain_schedules(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["list_domain_schedules"], domainId=domain_id
        )
        self.params = self._base_params(args)

    @decorator
    def list_domain_alerts(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["list_domain_alerts"], domainId=domain_id
        )
        self.params = self._base_params(args)

    @decorator
    def list_domain_assets(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["list_domain_assets"], domainId=domain_id
        )
        self.params = self._base_params(args)

    # Data Sources / Connections (domain-scoped — 2026-01-12-preview)
    # All data source operations require --domain-id and --data-source-id.
    # The old flat /connections path no longer exists in the API.
    @decorator
    def list_connections(self, args):
        """List data sources for a domain (alias for list_domain_data_sources)."""
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["list_domain_data_sources"], domainId=domain_id
        )
        self.params = self._base_params(args)

    @decorator
    def create_connection(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        data_source_id = self._first(args, "--data-source-id", self._first(args, "--connection-id", ""))
        self.method = "PUT"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["create_data_source"],
            domainId=domain_id,
            dataSourceId=data_source_id,
        )
        self.params = get_api_version_params("data_quality")
        self.payload = self._body_from_args(
            args,
            {
                "--name": "name",
                "--type": "dataSourceType",
                "--description": "description",
            },
        )

    @decorator
    def get_connection(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        data_source_id = self._first(args, "--data-source-id", self._first(args, "--connection-id", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["get_data_source"],
            domainId=domain_id,
            dataSourceId=data_source_id,
        )
        self.params = get_api_version_params("data_quality")

    @decorator
    def update_connection(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        data_source_id = self._first(args, "--data-source-id", self._first(args, "--connection-id", ""))
        self.method = "PUT"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["update_data_source"],
            domainId=domain_id,
            dataSourceId=data_source_id,
        )
        self.params = get_api_version_params("data_quality")
        self.payload = self._body_from_args(
            args,
            {
                "--name": "name",
                "--type": "dataSourceType",
                "--description": "description",
            },
        )

    @decorator
    def delete_connection(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        data_source_id = self._first(args, "--data-source-id", self._first(args, "--connection-id", ""))
        self.method = "DELETE"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["delete_data_source"],
            domainId=domain_id,
            dataSourceId=data_source_id,
        )
        self.params = get_api_version_params("data_quality")

    # Rules (domain-scoped — 2026-01-12-preview)
    @decorator
    def list_rules(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["list_rules_by_domain"], domainId=domain_id
        )
        self.params = self._base_params(args)

    @decorator
    def create_rule(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        self.method = "POST"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["create_rule"], domainId=domain_id
        )
        self.params = get_api_version_params("data_quality")
        payload = self._body_from_args(
            args,
            {
                "--name": "name",
                "--type": "type",
                "--description": "description",
                "--asset-id": "assetId",
                "--column": "columnName",
            },
        ) or {}
        threshold = self._float_param(args, "--threshold")
        if threshold is not None:
            payload["threshold"] = threshold
        self.payload = payload

    @decorator
    def get_rule(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        rule_id = self._first(args, "--rule-id", self._first(args, "ruleId", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["get_rule"], domainId=domain_id, ruleId=rule_id
        )
        self.params = get_api_version_params("data_quality")

    @decorator
    def update_rule(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        rule_id = self._first(args, "--rule-id", self._first(args, "ruleId", ""))
        self.method = "PUT"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["update_rule"], domainId=domain_id, ruleId=rule_id
        )
        self.params = get_api_version_params("data_quality")
        payload = self._body_from_args(
            args,
            {
                "--name": "name",
                "--type": "type",
                "--description": "description",
                "--asset-id": "assetId",
                "--column": "columnName",
            },
        ) or {}
        threshold = self._float_param(args, "--threshold")
        if threshold is not None:
            payload["threshold"] = threshold
        self.payload = payload

    @decorator
    def delete_rule(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        rule_id = self._first(args, "--rule-id", self._first(args, "ruleId", ""))
        self.method = "DELETE"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["delete_rule"], domainId=domain_id, ruleId=rule_id
        )
        self.params = get_api_version_params("data_quality")

    @decorator
    def apply_rule(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        rule_id = self._first(args, "--rule-id", self._first(args, "ruleId", ""))
        self.method = "POST"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["apply_rule"], domainId=domain_id, ruleId=rule_id
        )
        self.params = get_api_version_params("data_quality")
        payload = self._body_from_args(args) or {}
        asset_ids = self._list_param(args, "--asset-id")
        if asset_ids:
            payload["assetIds"] = asset_ids
        self.payload = payload

    # Profiles (domain/data-source scoped — 2026-01-12-preview)
    # Flat profile CRUD no longer exists. Profile = running data profiling on a data source.
    @decorator
    def run_profile(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        data_source_id = self._first(args, "--data-source-id", self._first(args, "--profile-id", ""))
        self.method = "POST"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["run_profile"],
            domainId=domain_id,
            dataSourceId=data_source_id,
        )
        self.params = get_api_version_params("data_quality")
        self.payload = self._body_from_args(args)

    @decorator
    def get_profile_results(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        data_source_id = self._first(args, "--data-source-id", self._first(args, "--profile-id", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["get_profile_results"],
            domainId=domain_id,
            dataSourceId=data_source_id,
        )
        self.params = self._base_params(args)

    # Schedules/Scans (domain-scoped — 2026-01-12-preview)
    # Scans are now schedules. All operations require --domain-id.
    # --scan-id is treated as --schedule-id for backward compat.
    @decorator
    def list_scans(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["list_scans"], domainId=domain_id
        )
        self.params = self._base_params(args)

    @decorator
    def create_scan(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        self.method = "POST"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["create_scan"], domainId=domain_id
        )
        self.params = get_api_version_params("data_quality")
        payload = self._body_from_args(
            args, {"--name": "name", "--schedule": "schedule"}
        ) or {}
        rule_ids = self._list_param(args, "--rule-id")
        if rule_ids:
            payload["ruleIds"] = rule_ids
        self.payload = payload

    @decorator
    def get_scan(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        schedule_id = self._first(args, "--schedule-id", self._first(args, "--scan-id", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["get_scan"], domainId=domain_id, scheduleId=schedule_id
        )
        self.params = get_api_version_params("data_quality")

    @decorator
    def update_scan(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        schedule_id = self._first(args, "--schedule-id", self._first(args, "--scan-id", ""))
        self.method = "PUT"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["update_scan"], domainId=domain_id, scheduleId=schedule_id
        )
        self.params = get_api_version_params("data_quality")
        payload = self._body_from_args(
            args, {"--name": "name", "--schedule": "schedule"}
        ) or {}
        rule_ids = self._list_param(args, "--rule-id")
        if rule_ids:
            payload["ruleIds"] = rule_ids
        self.payload = payload

    @decorator
    def delete_scan(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        schedule_id = self._first(args, "--schedule-id", self._first(args, "--scan-id", ""))
        self.method = "DELETE"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["delete_scan"], domainId=domain_id, scheduleId=schedule_id
        )
        self.params = get_api_version_params("data_quality")

    @decorator
    def run_scan(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        schedule_id = self._first(args, "--schedule-id", self._first(args, "--scan-id", ""))
        self.method = "POST"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["run_scan"], domainId=domain_id, scheduleId=schedule_id
        )
        self.params = get_api_version_params("data_quality")
        self.payload = self._body_from_args(args)

    @decorator
    def get_scan_results(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        schedule_id = self._first(args, "--schedule-id", self._first(args, "--scan-id", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["get_scan_results"], domainId=domain_id, scheduleId=schedule_id
        )
        self.params = self._base_params(args)

    @decorator
    def stop_scan(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", "")
        schedule_id = self._first(args, "--schedule-id", self._first(args, "--scan-id", ""))
        self.method = "POST"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["stop_scan"], domainId=domain_id, scheduleId=schedule_id
        )
        self.params = get_api_version_params("data_quality")
        self.payload = self._body_from_args(args)

    # Scores
    @decorator
    def get_quality_score(self, args):
        self._reset_request_state()
        asset_id = self._first(args, "--asset-id", self._first(args, "assetId", ""))
        self.method = "GET"
        self.endpoint = format_endpoint(
            ENDPOINTS["data_quality"]["get_quality_score"], assetId=asset_id
        )
        self.params = self._base_params(args)

    @decorator
    def list_asset_scores(self, args):
        self._reset_request_state()
        domain_id = self._first(args, "--domain-id", self._first(args, "domainId", ""))
        if domain_id:
            self.method = "GET"
            self.endpoint = format_endpoint(
                ENDPOINTS["data_quality"]["list_domain_assets"], domainId=domain_id
            )
            self.params = self._base_params(args)
            return

        self.method = "GET"
        self.endpoint = ENDPOINTS["data_quality"]["list_asset_scores"]
        self.params = self._base_params(args)
        product_id = self._first(args, "--product-id", "")
        threshold = self._float_param(args, "--threshold")
        if product_id:
            self.params["productId"] = product_id
        if threshold is not None:
            self.params["threshold"] = threshold
