# Spec: `generate_response()`

**File:** `generator.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user query and a list of retrieved rule chunks, generate a response that directly answers the question using only the retrieved text as context. The response must be grounded — it should not draw on the model's general knowledge of board games, only on what was retrieved.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's original question |
| `retrieved_chunks` | `list[dict]` | Ranked list of chunks from `retrieve()`, each with `"text"`, `"game"`, and `"distance"` |

**Output:** `str`

A plain string containing the response to show the user. The response should:
- Answer the question using only the retrieved rule text
- Identify which game the answer comes from
- Acknowledge clearly when the answer is not found in the loaded rules

Returns a fallback string (not an error) when `retrieved_chunks` is empty.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Context formatting

*How will you format the retrieved chunks before passing them to the LLM? Describe the structure — not the code. Consider: will you label chunks by game? Include distance scores? Separate chunks with delimiters?*

```
Format chunks as a numbered list with game labels:

1. [Game Name]
{chunk text}

2. [Game Name]
{chunk text}

Include all chunks retrieved (even low-relevance ones) so the LLM can assess 
which are actually useful. Include game names so the response can cite sources. 
Omit distance scores from the prompt — they're for system filtering, not LLM input.
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
You are a board game rules assistant. Answer questions using ONLY the rule 
text provided below. Do NOT use your general knowledge of board games.

If the answer is not found in the provided rules, respond exactly:
"I couldn't find that rule in the loaded rule books."

Do not speculate, infer, or fill in gaps with outside knowledge. Every claim 
in your response must be directly traceable to the provided text.
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
Always specify which game the answer comes from. Begin your response with:
"In [Game Name]: " followed by the rule text or direct quote.

If the answer spans multiple games, list each one: "In Catan: [answer]. 
In Monopoly: [answer]."

If no matching rule is found, do not guess or mention a game name.
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
Empty context (no chunks retrieved):
"I couldn't find that rule in the loaded rule books. Try rephrasing your question."

Low-relevance chunks (all distances > 0.7):
"I found rules in the system, but they don't seem to match your question. 
Try asking about specific mechanics like rolling, winning, or setup."

Chunks retrieved but model says "not found":
Trust the model — it evaluated relevance. Display the model's response as-is.
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
Pass ALL retrieved chunks to the LLM. Do NOT filter by distance threshold.

Rationale:
- The retriever ranks by relevance; the LLM is best positioned to judge final 
  relevance given the query context
- Hard filtering (e.g., distance < 0.5) risks removing valid results
- The grounding instruction tells the LLM to say "not found" if nothing is 
  relevant — trust it over a threshold

If chunks are genuinely irrelevant (distance > 0.7 for all results), log a 
warning but still attempt generation. The model may recognize patterns the 
retriever missed.
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
Messages structure:

[
  {
    "role": "system",
    "content": "[grounding instruction] [citation instruction]"
  },
  {
    "role": "user",
    "content": "[formatted context chunks]\n\nQuestion: [user query]"
  }
]

- System message: Both grounding and citation instructions (strict rules)
- User message: Context (numbered chunks with game labels) + the original query

This keeps guardrails separate from context, making the system prompt 
less ambiguous and easier to refine.
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: [your test query]
Response: [abbreviated response]
Correctly grounded? [yes / no]
Cited the right game? [yes / no]
```

**One thing you changed from your original spec after seeing the actual output:**

```
[your answer here]
```
