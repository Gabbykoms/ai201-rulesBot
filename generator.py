from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    TODO — Milestone 3:

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score (you can use this to filter weak matches)

    Before writing code, talk through these with your group:
      - How will you format the chunks into a context block for the prompt?
      - What instructions will stop the model from answering beyond what the
        rules say? (Grounding is the whole point — a confident wrong answer
        is worse than an honest "I don't know.")
      - How will you surface which game each answer comes from?

    Your response should:
      1. Answer using only the retrieved context — not the model's general knowledge
      2. Make clear which game the answer comes from
      3. Say so clearly when the answer isn't in the loaded rules

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    # Format chunks as a numbered list with game labels
    context = "RULE REFERENCES:\n\n"
    for i, chunk in enumerate(retrieved_chunks, 1):
        context += f"{i}. [{chunk['game']}]\n{chunk['text']}\n\n"

    # System prompt with grounding and citation instructions
    system_prompt = """You are a board game rules assistant. Answer questions using ONLY the rule text provided below. Do NOT use your general knowledge of board games.

If the answer is not found in the provided rules, respond exactly:
"I couldn't find that rule in the loaded rule books."

Do not speculate, infer, or fill in gaps with outside knowledge. Every claim in your response must be directly traceable to the provided text.

Always specify which game the answer comes from. Begin your response with:
"In [Game Name]: " followed by the rule text or direct quote.

If the answer spans multiple games, list each one: "In Catan: [answer]. In Monopoly: [answer]."

If no matching rule is found, do not guess or mention a game name."""

    # Build messages: system prompt + context + query
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"{context}\nQuestion: {query}"
        }
    ]

    # Call Groq API with low temperature for grounded, deterministic responses
    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0,
        max_tokens=500
    )

    return response.choices[0].message.content
