"""LOD API client with rate limiting, caching, and structured errors."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import quote, urlencode

import requests

try:
    from server.cache import cache
except ImportError:
    from cache import cache


LOD_API_BASE = "https://lod.lu/api"
REQUEST_TIMEOUT_SECONDS = 10
RETRY_DELAY_SECONDS = 0.5

# Rate limiting
_last_request_time = 0.0
_min_request_interval = 0.1


class LODAPIError(Exception):
    """Base error for LOD API failures."""

    error_type = "upstream_error"

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class LODTimeoutError(LODAPIError):
    error_type = "upstream_timeout"


class LODNetworkError(LODAPIError):
    error_type = "upstream_network_error"


class LODHTTPError(LODAPIError):
    error_type = "upstream_http_error"


class LODNotFoundError(LODAPIError):
    error_type = "not_found"


class LODInvalidResponseError(LODAPIError):
    error_type = "invalid_response"


def _rate_limited_request(url: str, headers: dict[str, str], retries: int = 1) -> requests.Response:
    """Make a rate-limited request to the LOD API, retrying transient failures once."""
    global _last_request_time

    for attempt in range(retries + 1):
        elapsed = time.time() - _last_request_time
        if elapsed < _min_request_interval:
            time.sleep(_min_request_interval - elapsed)

        _last_request_time = time.time()

        try:
            return requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.Timeout as exc:
            if attempt < retries:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise LODTimeoutError("LOD request timed out") from exc
        except requests.ConnectionError as exc:
            if attempt < retries:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise LODNetworkError("Could not reach the LOD API") from exc
        except requests.RequestException as exc:
            raise LODNetworkError(f"LOD request failed: {exc}") from exc

    raise LODNetworkError("LOD request failed")


def cached_api_call(endpoint: str, params: str, url: str) -> Any:
    """Make a cached API call with structured error handling."""
    cached = cache.get(endpoint, params)
    if cached is not None:
        return cached

    response = _rate_limited_request(url, {"accept": "application/json"})

    if response.status_code == 404:
        raise LODNotFoundError(f"LOD {endpoint} not found: {params}", status_code=404)
    if response.status_code != 200:
        raise LODHTTPError(
            f"LOD API returned HTTP {response.status_code}",
            status_code=response.status_code,
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise LODInvalidResponseError("LOD API returned invalid JSON") from exc

    cache.set(endpoint, params, data)
    return data


def search_api(query: str) -> Any:
    """Search for Luxembourgish words."""
    params = urlencode({"query": query, "lang": "lb"})
    url = f"{LOD_API_BASE}/en/search?{params}"
    return cached_api_call("search", params, url)


def suggest_api(prefix: str) -> Any:
    """Get autocomplete suggestions."""
    params = urlencode({"query": prefix})
    url = f"{LOD_API_BASE}/en/suggest?{params}"
    return cached_api_call("suggest", params, url)


def entry_api(lod_id: str) -> Any:
    """Get full entry details."""
    url = f"{LOD_API_BASE}/lb/entry/{quote(lod_id, safe='')}"
    return cached_api_call("entry", lod_id, url)
