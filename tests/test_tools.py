import pytest

from server import tools
from server.api import LODNotFoundError

RAW_ENTRY = {
    "entry": {
        "lemma": "Haus",
        "partOfSpeech": "SUBST",
        "ipa": "hæːʊs",
        "audioFiles": [{"ogg": "https://example.com/entry.ogg"}],
        "videos": [{"url": "https://example.com/sign.mp4"}],
        "microStructures": [
            {
                "grammaticalUnits": [
                    {
                        "meanings": [
                            {
                                "targetLanguages": {
                                    "en": {
                                        "parts": [
                                            {"type": "translation", "content": "house"},
                                            {"type": "semanticClarifier", "content": "building"},
                                        ]
                                    },
                                    "de": {
                                        "parts": [
                                            {"type": "translation", "content": "Haus"},
                                        ]
                                    },
                                },
                                "examples": [
                                    {
                                        "parts": [
                                            {
                                                "type": "text",
                                                "parts": [
                                                    {"type": "word", "content": "eist"},
                                                    {
                                                        "type": "inflectedHeadword",
                                                        "content": "Haus",
                                                    },
                                                ],
                                            }
                                        ]
                                    }
                                ],
                                "inflection": {
                                    "forms": [
                                        {"content": "Haiser"},
                                        {"content": "Haus"},
                                    ]
                                },
                            },
                            {
                                "targetLanguages": {
                                    "en": {
                                        "parts": [
                                            {"type": "translation", "content": "household"},
                                            {"type": "semanticClarifier", "content": "family"},
                                        ]
                                    }
                                },
                                "examples": [],
                                "inflection": {"forms": []},
                            },
                        ]
                    }
                ]
            }
        ],
    }
}


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    tools.cache.clear()
    yield
    tools.cache.clear()


def test_search_word_brief_normalizes_pos_labels(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        tools,
        "search_api",
        lambda word: {
            "results": [
                {"id": "HAUS1", "word_lb": "Haus", "pos": "SUBST+N"},
                {"id": "HAUSEN1", "word_lb": "hausen", "pos": "VRB"},
            ]
        },
    )

    assert tools.search_word_brief("haus") == {
        "HAUS1": "Haus (N)",
        "HAUSEN1": "hausen (V)",
    }


def test_autocomplete_filters_non_luxembourgish_items(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        tools,
        "suggest_api",
        lambda prefix: {
            "items": [
                {"word": "ha", "lang": "nl"},
                {"word": "hal", "lang": "lb"},
                {"word": "ham", "lang": "en"},
                {"word": "har", "lang": "lb"},
            ]
        },
    )

    assert tools.autocomplete("ha", limit=10) == "hal, har"


def test_get_entry_and_get_entries_share_the_same_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(tools, "entry_api", lambda lod_id: RAW_ENTRY)

    single = tools.get_entry("HAUS1", langs="en,de", max_examples=1)
    batch = tools.get_entries(["HAUS1"], langs="en,de", max_examples=1)

    assert single == {
        "id": "HAUS1",
        "w": "Haus",
        "pos": "SUBST",
        "ipa": "hæːʊs",
        "tr": {
            "en": "house building; household family",
            "de": "Haus",
        },
        "ex": ["eist Haus"],
        "infl": "Haiser, Haus",
        "audio": True,
        "sign": True,
    }
    assert batch == {"HAUS1": single}
    assert tools.get_def("HAUS1", "en") == "Haus: house building; household family"
    assert tools.get_defs(["HAUS1"], "en") == {"HAUS1": "Haus: house building; household family"}


def test_get_entry_returns_structured_error_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_not_found(lod_id: str):
        raise LODNotFoundError("LOD entry not found: UNKNOWN1", status_code=404)

    monkeypatch.setattr(tools, "entry_api", raise_not_found)

    assert tools.get_entry("UNKNOWN1") == {
        "error": {
            "type": "not_found",
            "message": "LOD entry not found: UNKNOWN1",
            "status": 404,
        }
    }
