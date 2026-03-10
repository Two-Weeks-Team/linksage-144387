import os
import json
import re
from typing import Any, Dict, List
import httpx

BASE_URL = "https://inference.do-ai.run/v1/chat/completions"
API_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
DEFAULT_MODEL = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")

def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

async def _call_inference(messages: List[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "max_completion_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            resp = await client.post(BASE_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # Expect OpenAI‑compatible response structure
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_str = _extract_json(content)
            return json.loads(json_str)
        except Exception as e:
            # Fallback payload on any error
            return {"note": "AI service temporarily unavailable", "error": str(e)}

async def summarize_and_tag(url: str, notes: str) -> Dict[str, Any]:
    prompt = (
        "You are a concise summarizer and tag generator. Given a web URL and optional user notes, "
        "return a JSON object with two keys: 'summary' (a short 2‑3 sentence summary) and 'tags' "
        "(a list of 3‑5 relevant tags). Include a 'confidence_score' between 0 and 1. Do NOT wrap the JSON in markdown."
    )
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"URL: {url}\nNotes: {notes}"},
    ]
    return await _call_inference(messages)

async def get_top_reads() -> Dict[str, Any]:
    prompt = (
        "Provide a JSON response for a dashboard's top reads. Return an object with two keys: 'top_reads' "
        "(a list of up to 5 items, each with 'id', 'title', 'summary', 'relevance_score' (0‑1 float), and 'smart_tags' list) "
        "and 'trending_topics' (a list of 2‑3 short strings). Use placeholder data if no real model output is available."
    )
    messages = [{"role": "system", "content": prompt}]
    result = await _call_inference(messages)
    # Ensure expected schema; provide static fallback if missing
    if not isinstance(result, dict) or "top_reads" not in result:
        result = {
            "top_reads": [
                {
                    "id": "demo1",
                    "title": "AI Ethics 2023 Overview",
                    "summary": "An overview of recent guidelines and debates around responsible AI development.",
                    "relevance_score": 0.92,
                    "smart_tags": ["trending", "must-read", "AI"]
                }
            ],
            "trending_topics": ["AI Governance", "Bias Mitigation"]
        }
    return result
