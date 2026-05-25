from server.cache import LODCache


def test_cache_records_hits_and_misses() -> None:
    cache = LODCache(ttl_seconds=3600, max_size=10)

    assert cache.get("search", "haus") is None

    payload = {"results": [{"id": "HAUS1"}]}
    cache.set("search", "haus", payload)

    assert cache.get("search", "haus") == payload
    assert cache.get_stats() == {
        "hits": 1,
        "misses": 1,
        "hit_rate": 50.0,
        "size": 1,
    }


def test_cache_evicts_oldest_entry_when_full() -> None:
    cache = LODCache(ttl_seconds=3600, max_size=1)
    haus_payload = {"results": [{"id": "HAUS1"}]}
    schoul_payload = {"results": [{"id": "SCHOUL1"}]}

    cache.set("search", "haus", haus_payload)
    cache.set("search", "schoul", schoul_payload)

    assert cache.get("search", "haus") is None
    assert cache.get("search", "schoul") == schoul_payload
