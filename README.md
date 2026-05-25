# LOD-MCP

A token-optimized Model Context Protocol (MCP) server for the [Luxembourgish Online Dictionary (LOD)](https://lod.lu).

This MCP server enables Claude to look up Luxembourgish words, get translations, and access dictionary data with minimal token usage.

## Features

- **Token-Efficient**: Returns compact data structures with short keys and optional fields
- **Cached**: 1-hour TTL cache reduces API calls and improves response times  
- **Rate-Limited**: Respects LOD API with 100ms intervals between requests
- **Resilient**: Retries transient upstream failures once and returns structured error payloads
- **Multi-Language**: Supports German (de), French (fr), English (en), Portuguese (pt), and Dutch (nl) translations
- **Batch Operations**: Look up multiple words/IDs in a single call (`search_words`, `get_entries`, `get_defs`)

## Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/Mohammed-Ashour/lod-mcp
cd lod-mcp
./install.sh
```

The install script will:

- ✓ Check Python version (3.13+ required)
- ✓ Create virtual environment
- ✓ Install the project and its dependencies
- ✓ Create a wrapper script that runs the installed CLI
- ✓ Test the installation
- ✓ Show Claude Desktop configuration

### Manual Installation

If you prefer manual setup:

**1. Prerequisites:**

install `uv` from [here](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or ensure pip is available

**2. Setup:**

```bash
git clone https://github.com/Mohammed-Ashour/lod-mcp
cd lod-mcp
```

**3. Create Virtual Environment:**

Using `uv`:

```bash
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python -e .
```

Or using standard Python:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -e .
```

**4. Create Wrapper Script:**

Create `run-mcp.sh`:

```bash
#!/bin/bash
export PYTHONUNBUFFERED=1
exec /path/to/lod-mcp/.venv/bin/lod-mcp
```

Make executable:

```bash
chmod +x run-mcp.sh
```

### Claude Desktop Configuration

Add to your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lod-mcp": {
      "command": "/path/to/lod-mcp/run-mcp.sh"
    }
  }
}
```

**Restart Claude Desktop** (Cmd+Q then reopen) to load the MCP server.

## Supported Tools

### 1. `search_word`

Search for Luxembourgish words and get entry IDs.

**Parameters:**

- `word` (str): The word to search
- `max_results` (int, optional): Max IDs to return (default: 5)

**Returns:** `List[str]` - LOD entry IDs (e.g., `["HAUS1", "HAUSEN1"]`)

**Example:**

```python
search_word("haus")  # Returns: ["HAUS1", "HAUSEN1"]
```

### 2. `search_word_brief`

Search with minimal preview info.

**Parameters:**

- `word` (str): The word to search
- `max_results` (int, optional): Max results (default: 3)

**Returns:** `Dict[str, str]` - Mapping ID to "word (POS)"

**Example:**

```python
search_word_brief("haus")  # Returns: {"HAUS1": "Haus (N)", "HAUSEN1": "hausen (V)"}
```

### 3. `autocomplete`

Get word suggestions.

**Parameters:**

- `prefix` (str): Partial word to complete
- `limit` (int, optional): Max suggestions (default: 5)

**Returns:** `str` - Comma-separated suggestions

**Example:**

```python
autocomplete("ha", limit=3)  # Returns: "haus, hausen, hausfrau"
```

### 4. `get_entry`

Get word details with configurable fields.

**Parameters:**

- `lod_id` (str): The LOD entry ID (e.g., "HAUS1")
- `langs` (str, optional): Comma-separated language codes (default: "de,fr,en")
- `max_examples` (int, optional): Max examples (default: 2, 0 to skip)

**Returns:** `Dict` - Compact dictionary with word data

**Example:**

```python
get_entry("HAUS1", langs="en,de", max_examples=1)
# Returns:
# {
#   "id": "HAUS1",
#   "w": "Haus",
#   "pos": "SUBST",
#   "ipa": "hæːʊs",
#   "tr": {"en": "house building", "de": "Haus Wohngebäude"},
#   "ex": ["mir hunn nach vill Aarbecht..."],
#   "infl": "Haiser, Haus",
#   "audio": true
# }
```

### 5. `get_def`

Get single-language definition as minimal string.

**Parameters:**

- `lod_id` (str): The LOD entry ID
- `lang` (str, optional): Language code (default: "en")

**Returns:** `str` - Definition string

**Example:**

```python
get_def("HAUS1", "en")  # Returns: "Haus: house building; house household, family"
```

---

## Batch Operations (Multi-Lookup Tools)

Use these tools when you need to look up **multiple words or IDs at once**. They reduce API calls and token usage compared to calling single-word tools repeatedly.

### `search_words` ⭐ RECOMMENDED

Search for multiple words simultaneously. Returns a dictionary mapping each input word to its search results.

**Parameters:**

- `words` (List[str]): List of words to search
- `max_results` (int, optional): Max results per word (default: 3)

**Returns:** `Dict[str, Dict[str, str]]` - `{word: {id: "word (POS)", ...}, ...}`

**Example:**

```python
search_words(["haus", "schoul", "bierg"])
# Returns:
# {
#   "haus": {"HAUS1": "Haus (N)", "HAUSEN1": "hausen (V)"},
#   "schoul": {"SCHOUL1": "Schoul (N)"},
#   "bierg": {"BIERG1": "Bierg (N)"}
# }
```

### `get_entries` ⭐ RECOMMENDED

Get full entry details for multiple LOD IDs at once.

**Parameters:**

- `lod_ids` (List[str]): List of LOD entry IDs
- `langs` (str, optional): Comma-separated language codes (default: "de,fr,en")
- `max_examples` (int, optional): Max examples per entry (default: 2)

**Returns:** `Dict[str, Dict]` - `{lod_id: entry_data, ...}`

**Example:**

```python
get_entries(["HAUS1", "SCHOUL1"], langs="en", max_examples=1)
# Returns:
# {
#   "HAUS1": {"id": "HAUS1", "w": "Haus", "pos": "SUBST", "tr": {"en": "house"}},
#   "SCHOUL1": {"id": "SCHOUL1", "w": "Schoul", "pos": "SUBST", "tr": {"en": "school"}}
# }
```

### `get_defs` ⭐ RECOMMENDED

Get minimal definitions for multiple LOD IDs at once.

**Parameters:**

- `lod_ids` (List[str]): List of LOD entry IDs
- `lang` (str, optional): Language code (default: "en")

**Returns:** `Dict[str, str]` - `{lod_id: "word: definition", ...}`

**Example:**

```python
get_defs(["HAUS1", "SCHOUL1"], lang="en")
# Returns:
# {
#   "HAUS1": "Haus: house building",
#   "SCHOUL1": "Schoul: school; school building"
# }
```

---

### 6. `cache_stats`

Get cache performance statistics.

**Returns:** `str` - Stats in format "hits/misses/rate% (size items)"

### 7. `cache_clear`

Clear the API response cache.

**Returns:** `str` - "OK"

## Usage Examples

> 💡 **Tip for AI Tools:** When looking up multiple words, always use batch tools (`search_words`, `get_entries`, `get_defs`) instead of calling single-word tools in a loop. They're faster and use fewer tokens and tool calls.

### Basic Word Lookup

1. **Search:**
  ```python
   ids = search_word("haus")  # ["HAUS1", "HAUSEN1"]
  ```
2. **Get definition:**
  ```python
   definition = get_def("HAUS1", "en")
   # "Haus: house building; house household..."
  ```

### Working with Verbs

```python
# Search for verb
ids = search_word("goen")

# Get full entry
entry = get_entry("GOEN1", langs="en", max_examples=1)
# Check entry["infl"] for conjugated forms
```

### Batch Lookup Example (Recommended)

```python
# Search multiple words at once
results = search_words(["haus", "schoul", "bierg"], max_results=2)
# Returns all results in one call

# Get definitions for multiple IDs
ids = ["HAUS1", "SCHOUL1", "BIERG1"]
defs = get_defs(ids, lang="en")

# Get full entries for multiple IDs
entries = get_entries(ids, langs="de,fr", max_examples=1)
```

## Using the LOD Skill (Non-MCP Tools)

If your AI tool doesn't support MCP, you can use the LOD skill directly. The skill provides the same functionality by making HTTP API calls to LOD.


### Skill Features

The skill provides structured guidance for:

- **Translation lookups** (de, fr, en, pt, nl)
- **Pronunciation** (IPA notation)
- **Conjugations** (complete verb tables)
- **Example sentences** with audio links
- **Batch operations** (efficient multi-word lookups)
- **Error handling** patterns


## Troubleshooting

### Installation Issues

**If the install script fails:**

```bash
# Check Python version
python3.13 --version  # Should be 3.13+

# Install uv (recommended package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Server won't start

1. Ensure the CLI exists: `.venv/bin/lod-mcp`
2. Ensure wrapper script is executable: `chmod +x run-mcp.sh`
3. Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log` (macOS)
4. Test manually: `./run-mcp.sh` - should output JSON

### Import errors

Reinstall the project into the virtual environment with `.venv/bin/python -m pip install -e .`.


### API errors?
- Check you're waiting 100ms between requests
- Verify word exists in Luxembourgish
- Test endpoints directly with curl

### Reinstalling

To start fresh:

```bash
./uninstall.sh  # Removes venv and wrapper
./install.sh    # Reinstalls everything
```

## API Source

Uses the public [LOD API](https://lod.lu/api/doc) provided by the Luxembourgish Ministry of Culture.

## License

MIT