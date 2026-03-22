import requests
import os
from dotenv import load_dotenv

load_dotenv()

import os
import streamlit as st

API_KEY = os.getenv("MISTRAL_API_KEY")


def explain_code(question, retrieved_chunks):

    if not retrieved_chunks:
        return "No relevant code found in the repository."

    # Build strict context
    context = "\n\n".join(
        f"""
File: {c['file_path']}
Lines: {c['start_line']}-{c['end_line']}

{c['content'][:800]}
"""
        for c in retrieved_chunks
    )

    prompt = f"""
You are an expert code analysis assistant.

IMPORTANT RULES:
- Use ONLY the provided repository context.
- Do NOT add external knowledge.
- First, briefly reason step-by-step about the request using the context.
- When identifying where something is handled (like authentication, APIs, etc.), ALWAYS list the HTTP route/endpoint in addition to the function name, if available.
- If the logic spans multiple files, connect them step by step.
- Explain how the code works using the retrieved snippets.
- If the answer is not present in the context, reply:
  "This information is not present in the repository."
- Keep the final answer concise (maximum 5 bullet points).
- Do NOT guess line numbers.

Repository Context:
{context}

Question:
{question}

Answer (bullet points only):


"""

    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "top_p": 1.0,
                "max_tokens": 600  # allow for reasoning
            },
            timeout=120
        )

        data = response.json()

        if "choices" not in data:
            return f"Error from LLM: {data}"

        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
      return f"DEBUG: {api_key}"
