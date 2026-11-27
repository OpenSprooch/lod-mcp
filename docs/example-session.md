# Example session

Recorded on 27 Nov 2026 against the live LOD API, with LOD-MCP at commit `ec68c45` and `mcp` 1.26.0. Nothing below is edited.

## In Claude Code

Claude Code (`claude -p`) with only LOD-MCP connected (`--strict-mcp-config`).

**Prompt:** How do I say 'I went' in Luxembourgish with goen, and what's the simple past? Look it up in the LOD. Answer in 2-3 short sentences.

**Tool call:** `search_word_brief` `{"word": "goen"}`

```json
{"result":{"GOEN1":"goen (V)","ZEGRONNGOEN1":"zegronn goen (V)","ZUGRONDGOEN1":"zugrond goen (V)"}}
```

**Tool call:** `get_conjugation` `{"lod_id": "GOEN1"}`

```json
{"id":"GOEN1","w":"goen","pos":"VRB","inf":"goen","pp":"gaangen / gaang","aux":"sinn","ind":{"prs":{"p1":"ginn","p2":"gees","p3":"geet","p4":"ginn","p5":"gitt","p6":"ginn"},"pst":{"p1":"goung","p2":"goungs","p3":"goung","p4":"goungen","p5":"goungt","p6":"goungen"},"pf":{"p1":"si gaangen / gaang","p2":"bass gaangen / gaang","p3":"ass gaangen / gaang","p4":"si gaangen / gaang","p5":"sidd gaangen / gaang","p6":"si gaangen / gaang"},"plf":{"p1":"war gaangen / gaang","p2":"waars gaangen / gaang","p3":"war gaangen / gaang","p4":"ware gaangen / gaang","p5":"waart gaangen / gaang","p6":"ware gaangen / gaang"}},"cnd":{"prs":{"p1":"géing","p2":"géings","p3":"géing","p4":"géingen","p5":"géingt","p6":"géingen"},"pf":{"p1":"géif / géing goen","p2":"géifs / géings goen","p3":"géif / géing goen","p4":"géifen / géinge goen","p5":"géift / géingt goen","p6":"géifen / géinge goen"},"plf":{"p1":"wier gaangen / gaang","p2":"wiers gaangen / gaang","p3":"wier gaangen / gaang","p4":"wiere gaangen / gaang","p5":"wiert gaangen / gaang","p6":"wiere gaangen / gaang"}},"imp":{"p2":"géi!","p5":"gitt!"},"sep":false}
```

**Answer:**

> **"I went" is usually *ech si gaangen*** (the perfect, with *sinn* as the auxiliary; the LOD also lists the participle *gaang*). **The simple past is *ech goung*.**

## Tool responses

The same server, called directly from an MCP client. JSON is indented here for reading; the server sends it compact.

### `search_words` `{"words": ["goen", "Gromper"]}`

```
{
  "goen": {
    "GOEN1": "goen (V)",
    "ZEGRONNGOEN1": "zegronn goen (V)",
    "ZUGRONDGOEN1": "zugrond goen (V)"
  },
  "Gromper": {
    "GROMPER1": "Gromper (N)"
  }
}
```

### `get_conjugation` `{"lod_id": "GOEN1"}`

```
{
  "id": "GOEN1",
  "w": "goen",
  "pos": "VRB",
  "inf": "goen",
  "pp": "gaangen / gaang",
  "aux": "sinn",
  "ind": {
    "prs": {
      "p1": "ginn",
      "p2": "gees",
      "p3": "geet",
      "p4": "ginn",
      "p5": "gitt",
      "p6": "ginn"
    },
    "pst": {
      "p1": "goung",
      "p2": "goungs",
      "p3": "goung",
      "p4": "goungen",
      "p5": "goungt",
      "p6": "goungen"
    },
    "pf": {
      "p1": "si gaangen / gaang",
      "p2": "bass gaangen / gaang",
      "p3": "ass gaangen / gaang",
      "p4": "si gaangen / gaang",
      "p5": "sidd gaangen / gaang",
      "p6": "si gaangen / gaang"
    },
    "plf": {
      "p1": "war gaangen / gaang",
      "p2": "waars gaangen / gaang",
      "p3": "war gaangen / gaang",
      "p4": "ware gaangen / gaang",
      "p5": "waart gaangen / gaang",
      "p6": "ware gaangen / gaang"
    }
  },
  "cnd": {
    "prs": {
      "p1": "géing",
      "p2": "géings",
      "p3": "géing",
      "p4": "géingen",
      "p5": "géingt",
      "p6": "géingen"
    },
    "pf": {
      "p1": "géif / géing goen",
      "p2": "géifs / géings goen",
      "p3": "géif / géing goen",
      "p4": "géifen / géinge goen",
      "p5": "géift / géingt goen",
      "p6": "géifen / géinge goen"
    },
    "plf": {
      "p1": "wier gaangen / gaang",
      "p2": "wiers gaangen / gaang",
      "p3": "wier gaangen / gaang",
      "p4": "wiere gaangen / gaang",
      "p5": "wiert gaangen / gaang",
      "p6": "wiere gaangen / gaang"
    }
  },
  "imp": {
    "p2": "géi!",
    "p5": "gitt!"
  },
  "sep": false
}
```

### `get_entry` `{"lod_id": "GROMPER1", "langs": "en,fr", "max_examples": 1}`

```
{
  "id": "GROMPER1",
  "w": "Gromper",
  "pos": "SUBST",
  "ipa": "ɡʀˈompɐ",
  "tr": {
    "fr": "pomme de terre; patate douce; montre (tape-à-l'œil) montre (de frimeur)",
    "en": "potato; sweet potato; flashy watch show-off watch"
  },
  "ex": [
    "de Bop ass amgaang, Gromperen ze schielen"
  ],
  "audio": true,
  "sign": true
}
```

### `autocomplete` `{"prefix": "schou"}`

```
schoul, schoun, schoulen, schounen, schounend
```

### `get_def` `{"lod_id": "GOEN1"}`

```
goen: to go to walk; to go to go to; to go for a purpose
```
