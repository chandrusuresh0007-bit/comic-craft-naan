import base64
import json
import re
from typing import Optional

import httpx

from app.config import settings
from app.services.catalog import enrich_item


# =========================================================
# Gemini REST endpoint
# =========================================================

def gemini_endpoint() -> str:

    return (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{settings.GEMINI_MODEL}:generateContent"
    )


# =========================================================
# JSON extraction
# =========================================================

def extract_json(
    text: str,
) -> Optional[dict]:

    text = text.strip()

    # Remove markdown fences.
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^```\s*",
        "",
        text,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to locate a JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:

        candidate = text[
            start : end + 1
        ]

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None

    return None


# =========================================================
# Prompt generation
# =========================================================

def build_prompt(
    planner: str,
    data: dict,
) -> str:

    if planner == "home":

        return f"""
You are PocketSmart AI, a budget-aware home interior
recommendation assistant.

User requirements:
{json.dumps(data, indent=2, ensure_ascii=False)}

Create a practical recommendation plan.

Important requirements:
1. Respect the user's total budget.
2. Recommend useful furniture, decor and lighting.
3. Prioritize the requested rooms.
4. Keep estimated prices realistic but clearly label them
   as estimates.
5. Do not claim live inventory or live prices.
6. Return exactly 6 recommendation items.
7. Include a category for every item.
8. Keep the total estimated item cost at or below the budget.
9. Include a short reason for every item.
10. Include practical money-saving tips.

Return ONLY valid JSON in this structure:

{{
  "summary": "short summary",
  "allocation": {{
    "furniture": 0,
    "decor": 0,
    "lighting": 0,
    "storage": 0
  }},
  "items": [
    {{
      "category": "furniture",
      "name": "product",
      "estimated_price": 0,
      "reason": "reason"
    }}
  ],
  "tips": [
    "tip 1",
    "tip 2"
  ]
}}
"""

    if planner == "party":

        return f"""
You are PocketSmart AI, a budget-aware party planning
assistant.

User requirements:
{json.dumps(data, indent=2, ensure_ascii=False)}

Create a practical party plan.

Important requirements:
1. Respect the total budget.
2. Consider guest count.
3. Recommend venue, food and decorations.
4. Include a realistic allocation.
5. Do not claim live availability.
6. Return exactly 6 recommendation items.
7. Keep estimated costs within budget.
8. Include a reason for each recommendation.
9. Include practical ways to reduce costs.

Return ONLY valid JSON:

{{
  "summary": "short summary",
  "allocation": {{
    "venue": 0,
    "food": 0,
    "decor": 0,
    "extras": 0
  }},
  "items": [
    {{
      "category": "venue",
      "name": "recommendation",
      "estimated_price": 0,
      "reason": "reason"
    }}
  ],
  "tips": [
    "tip 1",
    "tip 2"
  ]
}}
"""

    # Jewelry
    return f"""
You are PocketSmart AI, a budget-aware jewelry stylist.

User requirements:
{json.dumps(data, indent=2, ensure_ascii=False)}

Create a jewelry recommendation plan.

Important requirements:
1. Respect the jewelry budget.
2. Consider the occasion.
3. Consider style.
4. Consider preferred metal.
5. If an outfit image is supplied, use it to reason about
   color coordination and aesthetics.
6. Return exactly 6 jewelry recommendations.
7. Keep estimated prices within the budget.
8. Do not claim live inventory.
9. Include a reason for each item.
10. Include styling tips.

Return ONLY valid JSON:

{{
  "summary": "short summary",
  "allocation": {{
    "earrings": 0,
    "necklace": 0,
    "bracelet": 0,
    "ring": 0,
    "other": 0
  }},
  "items": [
    {{
      "category": "earrings",
      "name": "jewelry item",
      "estimated_price": 0,
      "reason": "reason"
    }}
  ],
  "tips": [
    "tip 1",
    "tip 2"
  ]
}}
"""


# =========================================================
# Gemini call
# =========================================================

def call_gemini(
    planner: str,
    data: dict,
    image_bytes: Optional[bytes] = None,
    image_mime_type: Optional[str] = None,
) -> Optional[dict]:

    if not settings.GEMINI_API_KEY:
        return None

    parts = [
        {
            "text": build_prompt(
                planner,
                data,
            )
        }
    ]

    # Optional multimodal image.
    if (
        image_bytes
        and image_mime_type
    ):

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        parts.append(
            {
                "inline_data": {
                    "mime_type": image_mime_type,
                    "data": encoded_image,
                }
            }
        )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json",
        },
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": settings.GEMINI_API_KEY,
    }

    try:

        with httpx.Client(
            timeout=60.0
        ) as client:

            response = client.post(
                gemini_endpoint(),
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            return None

        body = response.json()

        candidates = body.get(
            "candidates",
            [],
        )

        if not candidates:
            return None

        parts_response = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        text_parts = [
            part.get("text", "")
            for part in parts_response
            if part.get("text")
        ]

        if not text_parts:
            return None

        return extract_json(
            "\n".join(text_parts)
        )

    except (
        httpx.HTTPError,
        ValueError,
        KeyError,
        TypeError,
    ):
        return None


# =========================================================
# Safe price calculation
# =========================================================

def normalize_prices(
    items: list,
    budget: float,
) -> list:

    if not items:
        return []

    cleaned = []

    for item in items:

        try:
            price = float(
                item.get(
                    "estimated_price",
                    0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            price = 0

        if price < 0:
            price = 0

        cleaned.append(
            {
                "category": str(
                    item.get(
                        "category",
                        "general",
                    )
                ),
                "name": str(
                    item.get(
                        "name",
                        "Recommended item",
                    )
                ),
                "estimated_price": price,
                "reason": str(
                    item.get(
                        "reason",
                        "Fits the selected requirements.",
                    )
                ),
            }
        )

    total = sum(
        item["estimated_price"]
        for item in cleaned
    )

    # If AI overshoots budget, scale prices down.
    if total > budget and total > 0:

        factor = (
            budget * 0.95
        ) / total

        for item in cleaned:
            item["estimated_price"] = round(
                item["estimated_price"]
                * factor,
                2,
            )

    return cleaned


# =========================================================
# Fallback recommendations
# =========================================================

def fallback_home(
    data: dict,
) -> dict:

    budget = float(
        data["budget"]
    )

    rooms = data.get(
        "rooms",
        ["living room"],
    )

    room = rooms[0]

    allocations = {
        "furniture": round(
            budget * 0.40,
            2,
        ),
        "decor": round(
            budget * 0.20,
            2,
        ),
        "lighting": round(
            budget * 0.15,
            2,
        ),
        "storage": round(
            budget * 0.25,
            2,
        ),
    }

    raw_items = [
        (
            "furniture",
            f"{data.get('style', 'modern').title()} "
            f"{room.title()} Seating",
            allocations["furniture"],
            "Creates the main functional foundation for the room.",
        ),
        (
            "furniture",
            "Compact Accent Table",
            budget * 0.10,
            "Adds useful surface space without consuming too much budget.",
        ),
        (
            "decor",
            "Decorative Wall Art Set",
            budget * 0.08,
            "Adds personality while remaining budget friendly.",
        ),
        (
            "lighting",
            "Warm LED Floor Lamp",
            allocations["lighting"],
            "Improves ambience and functional lighting.",
        ),
        (
            "storage",
            "Modular Storage Unit",
            budget * 0.15,
            "Adds organized storage for everyday items.",
        ),
        (
            "decor",
            "Indoor Decorative Plant",
            budget * 0.07,
            "Adds a natural visual element to the space.",
        ),
    ]

    items = [
        enrich_item(
            "home",
            category,
            name,
            price,
            reason,
        )
        for category, name, price, reason
        in raw_items
    ]

    return {
        "planner": "home",
        "budget": budget,
        "allocation": allocations,
        "summary": (
            f"A practical {data.get('style', 'modern')} "
            f"setup for {', '.join(rooms)}."
        ),
        "items": items,
        "tips": [
            "Buy large furniture first and decorate around it.",
            "Use warm LED lighting to improve ambience economically.",
            "Compare marketplace prices before purchasing.",
            "Prefer multifunctional storage when space is limited.",
        ],
        "source_mode": "fallback",
    }


def fallback_party(
    data: dict,
) -> dict:

    budget = float(
        data["budget"]
    )

    guests = int(
        data["guests"]
    )

    allocations = {
        "venue": round(
            budget * 0.30,
            2,
        ),
        "food": round(
            budget * 0.40,
            2,
        ),
        "decor": round(
            budget * 0.15,
            2,
        ),
        "extras": round(
            budget * 0.15,
            2,
        ),
    }

    raw_items = [
        (
            "venue",
            f"Event venue for {guests} guests",
            allocations["venue"],
            "Keeps the venue allocation predictable.",
        ),
        (
            "food",
            f"{data.get('food_preference', 'mixed').title()} "
            "food package",
            allocations["food"],
            "Provides the largest share of the party budget for guests.",
        ),
        (
            "food",
            "Beverage and snack arrangement",
            budget * 0.10,
            "Provides convenient refreshments between meals.",
        ),
        (
            "decor",
            "Theme decoration package",
            allocations["decor"],
            "Creates a cohesive event atmosphere.",
        ),
        (
            "extras",
            "Music and entertainment setup",
            budget * 0.08,
            "Adds entertainment while controlling spending.",
        ),
        (
            "extras",
            "Party supplies and contingency",
            budget * 0.07,
            "Covers small unexpected requirements.",
        ),
    ]

    items = [
        enrich_item(
            "party",
            category,
            name,
            price,
            reason,
        )
        for category, name, price, reason
        in raw_items
    ]

    return {
        "planner": "party",
        "budget": budget,
        "allocation": allocations,
        "summary": (
            f"A balanced {data.get('event_type', 'party')} "
            f"plan for approximately {guests} guests."
        ),
        "items": items,
        "tips": [
            "Book the venue before spending heavily on decoration.",
            "Use a per-person food budget to avoid overspending.",
            "Choose reusable decorations where possible.",
            "Keep a small contingency amount for last-minute expenses.",
        ],
        "source_mode": "fallback",
    }


def fallback_jewelry(
    data: dict,
) -> dict:

    budget = float(
        data["budget"]
    )

    allocations = {
        "earrings": round(
            budget * 0.25,
            2,
        ),
        "necklace": round(
            budget * 0.35,
            2,
        ),
        "bracelet": round(
            budget * 0.15,
            2,
        ),
        "ring": round(
            budget * 0.15,
            2,
        ),
        "other": round(
            budget * 0.10,
            2,
        ),
    }

    metal = data.get(
        "metal",
        "any",
    )

    style = data.get(
        "style",
        "elegant",
    )

    occasion = data.get(
        "occasion",
        "special occasion",
    )

    raw_items = [
        (
            "earrings",
            f"{style.title()} {metal.title()} Earrings",
            allocations["earrings"],
            f"Designed for an {occasion} while matching the requested style.",
        ),
        (
            "necklace",
            f"{style.title()} Statement Necklace",
            allocations["necklace"],
            "Provides a focal point without requiring a full jewelry set.",
        ),
        (
            "bracelet",
            "Minimal Bracelet",
            allocations["bracelet"],
            "Adds a subtle coordinated accent.",
        ),
        (
            "ring",
            "Classic Cocktail Ring",
            allocations["ring"],
            "Adds visual interest while remaining within the plan.",
        ),
        (
            "other",
            "Matching Jewelry Set",
            allocations["other"],
            "Useful when a coordinated look is preferred.",
        ),
        (
            "earrings",
            "Simple Everyday Studs",
            budget * 0.05,
            "A versatile lower-cost alternative.",
        ),
    ]

    items = [
        enrich_item(
            "jewelry",
            category,
            name,
            price,
            reason,
        )
        for category, name, price, reason
        in raw_items
    ]

    return {
        "planner": "jewelry",
        "budget": budget,
        "allocation": allocations,
        "summary": (
            f"{style.title()} jewelry ideas for a "
            f"{occasion} occasion using a {metal} preference."
        ),
        "items": items,
        "tips": [
            "Choose one statement piece and keep other pieces simpler.",
            "Match jewelry tones with the outfit rather than buying a complete set automatically.",
            "Compare prices across marketplaces before purchasing.",
            "Reserve part of the budget for a versatile everyday piece.",
        ],
        "source_mode": "fallback",
    }


# =========================================================
# Convert Gemini result
# =========================================================

def process_gemini_result(
    planner: str,
    data: dict,
    ai_result: dict,
) -> Optional[dict]:

    if not isinstance(
        ai_result,
        dict,
    ):
        return None

    budget = float(
        data["budget"]
    )

    ai_items = ai_result.get(
        "items",
        [],
    )

    if not isinstance(
        ai_items,
        list,
    ):
        return None

    ai_items = normalize_prices(
        ai_items,
        budget,
    )

    if len(ai_items) < 3:
        return None

    items = [
        enrich_item(
            planner,
            item["category"],
            item["name"],
            item["estimated_price"],
            item["reason"],
        )
        for item in ai_items[:8]
    ]

    allocation = ai_result.get(
        "allocation",
        {},
    )

    if not isinstance(
        allocation,
        dict,
    ):
        allocation = {}

    tips = ai_result.get(
        "tips",
        [],
    )

    if not isinstance(
        tips,
        list,
    ):
        tips = []

    return {
        "planner": planner,
        "budget": budget,
        "allocation": {
            str(key): round(
                float(value),
                2,
            )
            for key, value in allocation.items()
            if isinstance(
                value,
                (int, float),
            )
        },
        "summary": str(
            ai_result.get(
                "summary",
                "Personalized recommendations generated by PocketSmart AI.",
            )
        ),
        "items": items,
        "tips": [
            str(tip)
            for tip in tips[:8]
        ],
        "source_mode": "gemini",
    }


# =========================================================
# Public generation function
# =========================================================

def generate_recommendations(
    planner: str,
    data: dict,
    image_bytes: Optional[bytes] = None,
    image_mime_type: Optional[str] = None,
) -> dict:

    planner = planner.lower().strip()

    ai_result = call_gemini(
        planner=planner,
        data=data,
        image_bytes=image_bytes,
        image_mime_type=image_mime_type,
    )

    if ai_result:

        processed = process_gemini_result(
            planner,
            data,
            ai_result,
        )

        if processed:
            return processed

    # Fallback.
    if planner == "home":
        return fallback_home(data)

    if planner == "party":
        return fallback_party(data)

    if planner == "jewelry":
        return fallback_jewelry(data)

    raise ValueError(
        f"Unsupported planner: {planner}"
    )
