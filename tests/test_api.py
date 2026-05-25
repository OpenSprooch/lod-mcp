import pytest
import requests

from server import api


class StubResponse:
    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


@pytest.fixture(autouse=True)
def reset_api_state() -> None:
    api.cache.clear()
    api._last_request_time = 0.0
    yield
    api.cache.clear()
    api._last_request_time = 0.0


def test_search_api_url_encodes_unicode_and_uses_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_get(url: str, headers: dict[str, str], timeout: int):
        calls.append(url)
        return StubResponse(200, {"results": [{"id": "SEIER2"}]})

    monkeypatch.setattr(api.requests, "get", fake_get)
    monkeypatch.setattr(api.time, "sleep", lambda _: None)

    assert api.search_api("séier") == {"results": [{"id": "SEIER2"}]}
    assert api.search_api("séier") == {"results": [{"id": "SEIER2"}]}
    assert calls == ["https://lod.lu/api/en/search?query=s%C3%A9ier&lang=lb"]


def test_entry_api_retries_timeout_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"count": 0}

    def fake_get(url: str, headers: dict[str, str], timeout: int):
        calls["count"] += 1
        if calls["count"] == 1:
            raise requests.Timeout("slow upstream")
        return StubResponse(200, {"entry": {"lemma": "Haus"}})

    monkeypatch.setattr(api.requests, "get", fake_get)
    monkeypatch.setattr(api.time, "sleep", lambda _: None)

    assert api.entry_api("HAUS1") == {"entry": {"lemma": "Haus"}}
    assert calls["count"] == 2


def test_entry_api_raises_structured_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, headers: dict[str, str], timeout: int):
        return StubResponse(404, {})

    monkeypatch.setattr(api.requests, "get", fake_get)
    monkeypatch.setattr(api.time, "sleep", lambda _: None)

    with pytest.raises(api.LODNotFoundError) as exc_info:
        api.entry_api("UNKNOWN1")

    assert exc_info.value.error_type == "not_found"
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "LOD entry not found: UNKNOWN1"
