# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's natural language question |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |

**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:

| Key | Type | Description |
|-----|------|-------------|
| `"text"` | `str` | The chunk text |
| `"game"` | `str` | The game name this chunk came from |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |

Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Query approach

*Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?*

```
Use _collection.query() with:
- query_texts=[query] — pass the user's natural language question
- n_results=n_results — limit results to the specified count
- include=["documents", "metadatas", "distances"] — fetch text, game name, and relevance scores

We use query_texts (not query_embeddings) because the collection will embed the query for us internally, keeping the code simpler and consistent with Chroma's typical usage pattern.
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
{
    "text": "Players collect resources by rolling dice...",
    "game": "Catan",
    "distance": 0.23
}

- "text" comes from results["documents"][0][i]
- "game" comes from results["metadatas"][0][i]["game"]
- "distance" comes from results["distances"][0][i]
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
Access results["documents"][0] to get the actual list of chunks.

The nesting exists because _collection.query() is designed to handle batch queries — 
you can pass multiple query_texts at once and get back results for each. Since we're 
only querying once, we always index [0] to get the results for our single query.
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
Return all n_results regardless of distance (no filtering).

Tradeoffs:
- No filtering: Simple, gives generate_response() full context to work with; 
  risks including loosely-related chunks that might confuse the answer
- With filtering: Only includes high-confidence matches; risks returning too few 
  results if the query is ambiguous or niche

Decision: No filtering. Let generate_response() decide what's useful; 
the LLM can ignore weak matches in its reasoning.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
(a) Empty collection: returns [] (Chroma handles this gracefully)

(b) No good matches: returns n_results chunks with high distance scores 
    (e.g., 0.8+). generate_response() will see weak context and can say 
    "I couldn't find relevant rules"

(c) Multi-game matches: Works naturally — metadatas includes the game name 
    for each result, so generate_response() knows which game each chunk is from
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: "How do you set up the board in Catan?"
Top result game: Catan
Distance score: 0.380
Does it make sense? Yes — the top result is the OVERVIEW section of Catan's 
official rules, which contains board setup information. Strong semantic match 
confirms the retriever correctly identified game-relevant content.
```

**One thing about the query results that surprised you:**

```
The retriever successfully disambiguates game-specific queries even when 
queries mention game names explicitly. For example, "How do you get out of 
Jail in Monopoly?" returns Monopoly chunks with low distance scores (0.367), 
while "what happens when you roll a 7?" correctly identifies Catan as the 
relevant game (despite 7 being important in many games). Cross-game matches 
show low confidence (0.6+) compared to correct-game matches (0.3–0.4), so 
the semantic search naturally prioritizes the right game.
```
