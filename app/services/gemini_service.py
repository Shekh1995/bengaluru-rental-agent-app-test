import os
from typing import List

import httpx

from app.models import PropertyListing


class GeminiServiceError(RuntimeError):
    pass


class GeminiService:
    @staticmethod
    def answer(question: str, listings: List[PropertyListing]) -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise GeminiServiceError("GEMINI_API_KEY is not configured")

        model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        context = "\n".join(
            f"- {item.title} | {item.area} | {item.bhk} BHK | rent ₹{item.rent_monthly} | "
            f"deposit ₹{item.deposit} | furnishing {item.furnishing}"
            for item in listings[:10]
        ) or "No matching listings are available."
        prompt = (
            "You are a practical Bengaluru rental advisor. Answer the user's question using only "
            "the listing context below. Do not invent availability, prices, or facts. Keep the answer "
            "under 120 words and mention the listing title when making a recommendation.\n\n"
            f"Listing context:\n{context}\n\nUser question: {question}"
        )
        try:
            response = httpx.post(
                endpoint,
                params={"key": api_key},
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30.0,
            )
            response.raise_for_status()
            payload = response.json()
            answer = payload["candidates"][0]["content"]["parts"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
            raise GeminiServiceError(f"Gemini request failed: {error}") from error
        return answer.strip()