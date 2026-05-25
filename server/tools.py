"""MCP tool definitions."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

try:
    from server.api import LODAPIError, entry_api, search_api, suggest_api
    from server.cache import cache
    from server.pos import normalize_pos
    from server.projections import project_definition, project_entry
except ImportError:
    from api import LODAPIError, entry_api, search_api, suggest_api
    from cache import cache
    from pos import normalize_pos
    from projections import project_definition, project_entry

mcp = FastMCP("lod-mcp")


def _tool_error(error: LODAPIError) -> dict[str, Any]:
    """Convert upstream exceptions into compact MCP error payloads."""
    payload: dict[str, Any] = {
        "type": error.error_type,
        "message": error.message,
    }
    if error.status_code is not None:
        payload["status"] = error.status_code
    return {"error": payload}


def _brief_results(items: list[dict[str, Any]], max_results: int) -> dict[str, str]:
    """Build compact search previews."""
    results: dict[str, str] = {}
    for item in items[:max_results]:
        lod_id = item.get("id")
        word_text = item.get("word_lb")
        pos_short = normalize_pos(item.get("pos"))
        if lod_id and word_text:
            results[lod_id] = f"{word_text} ({pos_short})" if pos_short else word_text
    return results


@mcp.tool()
def search_word(word: str, max_results: int = 5) -> list[str] | dict[str, Any]:
    """
    Search for Luxembourgish words and return LOD entry IDs.

    Args:
        word: The word to search for (case-insensitive)
        max_results: Max IDs to return (default: 5)

    Returns:
        List of LOD entry IDs (e.g., ['HAUS1', 'HAUSEN1'])
    """
    try:
        data = search_api(word)
    except LODAPIError as error:
        return _tool_error(error)

    ids = [item.get("id") for item in data.get("results", []) if item.get("id")]
    return ids[:max_results]


@mcp.tool()
def search_word_brief(word: str, max_results: int = 3) -> dict[str, str] | dict[str, Any]:
    """
    Search for words returning minimal preview as key-value pairs.

    Args:
        word: Word to search
        max_results: Max results (default: 3)

    Returns:
        Dict mapping ID to "word (POS)" format
    """
    try:
        data = search_api(word)
    except LODAPIError as error:
        return _tool_error(error)

    return _brief_results(data.get("results", []), max_results)


@mcp.tool()
def search_words(
    words: list[str],
    max_results: int = 3,
) -> dict[str, dict[str, str] | dict[str, Any]]:
    """
    Search for multiple words at once and return results for each.

    Args:
        words: List of words to search
        max_results: Max results per word (default: 3)

    Returns:
        Dictionary mapping each input word to its search results
        Format: {"word": {"ID1": "word (POS)", "ID2": "word (POS)"}}
    """
    results: dict[str, dict[str, str] | dict[str, Any]] = {}
    for word in words:
        try:
            data = search_api(word)
        except LODAPIError as error:
            results[word] = _tool_error(error)
            continue

        results[word] = _brief_results(data.get("results", []), max_results)

    return results


@mcp.tool()
def autocomplete(prefix: str, limit: int = 5) -> str | dict[str, Any]:
    """
    Get word suggestions as comma-separated string.

    Args:
        prefix: Partial word to complete
        limit: Max suggestions (default: 5)

    Returns:
        Comma-separated string, e.g.: "haus, hausen, hausfrau"
    """
    limit = min(limit, 10)
    try:
        data = suggest_api(prefix)
    except LODAPIError as error:
        return _tool_error(error)

    seen = set()
    words: list[str] = []
    for item in data.get("items", []):
        if item.get("lang") != "lb":
            continue

        word = item.get("word")
        if word and word not in seen:
            seen.add(word)
            words.append(word)
            if len(words) >= limit:
                break

    return ", ".join(words)


@mcp.tool()
def get_entry(lod_id: str, langs: str = "de,fr,en", max_examples: int = 2) -> dict[str, Any]:
    """
    Get word details with configurable fields to minimize tokens.

    Args:
        lod_id: The LOD entry ID
        langs: Comma-separated language codes (default: "de,fr,en")
        max_examples: Max examples to return (default: 2, 0 to skip)

    Returns:
        Compact dictionary with only requested data
    """
    try:
        data = entry_api(lod_id)
    except LODAPIError as error:
        return _tool_error(error)

    return project_entry(data, lod_id, langs=langs, max_examples=max_examples)


@mcp.tool()
def get_entries(
    lod_ids: list[str],
    langs: str = "de,fr,en",
    max_examples: int = 2,
) -> dict[str, dict[str, Any]]:
    """
    Get word details for multiple LOD entry IDs at once.

    Args:
        lod_ids: List of LOD entry IDs to look up
        langs: Comma-separated language codes (default: "de,fr,en")
        max_examples: Max examples per entry (default: 2, 0 to skip)

    Returns:
        Dictionary mapping each LOD ID to its entry data
        Format: {"HAUS1": {"w": "Haus", "pos": "SUBST", "tr": {...}}, "HAUSEN1": {...}}
    """
    results: dict[str, dict[str, Any]] = {}
    for lod_id in lod_ids:
        try:
            data = entry_api(lod_id)
        except LODAPIError as error:
            results[lod_id] = _tool_error(error)
            continue

        results[lod_id] = project_entry(data, lod_id, langs=langs, max_examples=max_examples)

    return results


@mcp.tool()
def get_def(lod_id: str, lang: str = "en") -> str | dict[str, Any]:
    """
    Get single-language definition as string (minimal tokens).

    Args:
        lod_id: The LOD entry ID
        lang: Single language code (default: "en")

    Returns:
        Definition string or error message
    """
    try:
        data = entry_api(lod_id)
    except LODAPIError as error:
        return _tool_error(error)

    return project_definition(data, lod_id, lang=lang)


@mcp.tool()
def get_defs(lod_ids: list[str], lang: str = "en") -> dict[str, str | dict[str, Any]]:
    """
    Get single-language definitions for multiple LOD entry IDs at once.

    Args:
        lod_ids: List of LOD entry IDs to look up
        lang: Single language code (default: "en")

    Returns:
        Dictionary mapping each LOD ID to its definition string
        Format: {"HAUS1": "Haus: house building", "HAUSEN1": "hausen: to live"}
    """
    results: dict[str, str | dict[str, Any]] = {}
    for lod_id in lod_ids:
        try:
            data = entry_api(lod_id)
        except LODAPIError as error:
            results[lod_id] = _tool_error(error)
            continue

        results[lod_id] = project_definition(data, lod_id, lang=lang)

    return results


@mcp.tool()
def cache_stats() -> str:
    """Get cache statistics as compact string."""
    stats = cache.get_stats()
    return f"{stats['hits']}/{stats['misses']}/{stats['hit_rate']}% ({stats['size']} items)"


@mcp.tool()
def cache_clear() -> str:
    """Clear the cache."""
    cache.clear()
    return "OK"
