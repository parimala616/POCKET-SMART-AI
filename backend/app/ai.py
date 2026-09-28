import json
import re

from typing import Any

from google import genai
from google.genai import types

from .config import settings
from .links import links


HOME_PLATFORMS = [
    "amazon",
    "flipkart",
    "ikea"
]


PARTY_PLATFORMS = [
    "amazon",
    "flipkart",
    "swiggy",
    "zomato",
    "booking",
    "makemytrip",
    "oyorooms"
]


JEWELRY_PLATFORMS = [
    "amazon",
    "flipkart",
    "tanishq",
    "caratlane",
    "bluestone",
    "myntra",
    "meesho"
]


def _extract_json(text: str) -> dict[str, Any]:

    text = (text or "").strip()

    text = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        text,
        flags=re.I | re.S
    )

    try:

        return json.loads(text)

    except json.JSONDecodeError:

        start = text.find("{")
        end = text.rfind("}")

        if start >= 0 and end > start:

            return json.loads(
                text[start:end + 1]
            )

        raise


def _call(
    prompt: str,
    image_bytes: bytes | None = None,
    mime_type: str | None = None
) -> dict[str, Any]:

    if not settings.gemini_api_key:
        return {}

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    contents: Any = prompt

    if image_bytes:

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type or "image/jpeg"
        )

        contents = [
            prompt,
            image_part
        ]

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4,
            max_output_tokens=5000
        )
    )

    return _extract_json(
        response.text
    )


def _finalize(
    result: dict[str, Any],
    planner: str,
    budget: float,
    platforms: list[str]
) -> dict[str, Any]:

    result["planner"] = planner

    result["total_budget"] = float(
        budget
    )

    breakdown = (
        result.get("budget_breakdown")
        or []
    )

    total = 0.0

    calculation_table = []

    for category in breakdown:

        category.setdefault(
            "items",
            []
        )

        calculated_allocation = 0.0

        for item in category["items"]:

            item.setdefault(
                "quantity",
                1
            )

            item["estimated_price"] = max(
                0.0,
                float(
                    item.get(
                        "estimated_price",
                        0
                    )
                )
            )

            quantity = max(
                1,
                int(
                    item.get(
                        "quantity",
                        1
                    )
                )
            )

            item["quantity"] = quantity

            calculated_allocation += (
                item["estimated_price"]
                * quantity
            )

            search_terms = item.get(
                "search_terms",
                item.get("name", "")
            )

            item["search_terms"] = (
                search_terms
            )

            item["shopping_links"] = links(
                search_terms,
                platforms
            )

        requested_allocation = float(
            category.get(
                "allocation",
                calculated_allocation
            )
        )

        category["allocation"] = round(
            min(
                requested_allocation,
                budget
            ),
            2
        )

        total += category["allocation"]

        calculation_table.append({
            "category": category.get(
                "category",
                "Other"
            ),
            "items_count": len(
                category["items"]
            ),
            "total_cost": round(
                category["allocation"],
                2
            ),
            "percentage_of_budget": round(
                (
                    category["allocation"]
                    / budget
                    * 100
                )
                if budget
                else 0,
                2
            )
        })

    # Protect the user from an over-budget AI response.
    if total > budget and total > 0:

        scale = budget / total

        for category in breakdown:

            for item in category["items"]:

                item["estimated_price"] = round(
                    item["estimated_price"]
                    * scale,
                    2
                )

        total = budget

    result["budget_breakdown"] = breakdown

    result["remaining_budget"] = round(
        max(0, budget - total),
        2
    )

    result["calculation_table_inr"] = (
        calculation_table
    )

    result.setdefault(
        "additional_suggestions",
        []
    )

    result.setdefault(
        "styling_tips",
        []
    )

    return result


# =========================================================
# HOME
# =========================================================

def home(budget_input) -> dict[str, Any]:

    prompt = f"""
You are PocketSmart AI, an India-focused budget
planning assistant.

Create a practical home interior budget plan.

Currency:
INR

Budget:
{budget_input.total_budget}

Number of lights:
{budget_input.num_lights}

Number of ceiling fans:
{budget_input.num_fans}

Furniture pieces:
{budget_input.num_furniture}

Dining tables:
{budget_input.num_dining_tables}

Living room:
{budget_input.has_living_room}

Kitchen:
{budget_input.has_kitchen}

Bedroom:
{budget_input.has_bedroom}

Additional requirements:
{budget_input.additional_requirements or "None"}

Return ONLY valid JSON.

Use exactly this general structure:

{{
  "budget_breakdown": [
    {{
      "category": "Lighting",
      "allocation": 1000,
      "items": [
        {{
          "name": "Product",
          "description": "Description",
          "estimated_price": 500,
          "quantity": 2,
          "search_terms": "search phrase"
        }}
      ]
    }}
  ],
  "additional_suggestions": [
    "Suggestion"
  ]
}}

Important:

- Keep recommendations practical.
- Use Indian context.
- Stay within the given budget.
- Do not invent exact live prices.
- Prices are estimates.
- Prioritize essentials.
"""

    result = _call(prompt)

    if not result:

        result = {
            "budget_breakdown": [

                {
                    "category": "Lighting",

                    "items": [
                        {
                            "name": "Warm LED bulbs",

                            "description":
                                "Energy-efficient "
                                "general lighting",

                            "estimated_price": 300,

                            "quantity": max(
                                1,
                                budget_input.num_lights
                            ),

                            "search_terms":
                                "warm white LED bulb India"
                        }
                    ]
                },

                {
                    "category": "Ceiling Fans",

                    "items": [
                        {
                            "name":
                                "Energy-efficient "
                                "ceiling fan",

                            "description":
                                "Standard room "
                                "ceiling fan",

                            "estimated_price": 1800,

                            "quantity": max(
                                1,
                                budget_input.num_fans
                            ),

                            "search_terms":
                                "energy efficient ceiling fan India"
                        }
                    ]
                },

                {
                    "category": "Furniture",

                    "items": [
                        {
                            "name":
                                "Compact "
                                "multipurpose table",

                            "description":
                                "Simple table for "
                                "living room or "
                                "study use",

                            "estimated_price": 3500,

                            "quantity": max(
                                1,
                                budget_input.num_furniture
                            ),

                            "search_terms":
                                "compact wooden table India"
                        }
                    ]
                }
            ],

            "additional_suggestions": [
                "Prioritize essential pieces first.",
                "Compare dimensions and warranty before buying."
            ]
        }

    return _finalize(
        result,
        "home",
        budget_input.total_budget,
        HOME_PLATFORMS
    )


# =========================================================
# PARTY
# =========================================================

def party(budget_input) -> dict[str, Any]:

    prompt = f"""
You are PocketSmart AI.

Create an India-specific party budget plan.

Total budget:
{budget_input.total_budget}

Party type:
{budget_input.party_type}

Number of guests:
{budget_input.num_guests}

Venue:
{budget_input.venue_type or "Not specified"}

Catering:
{budget_input.needs_catering}

Decoration:
{budget_input.needs_decoration}

Entertainment:
{budget_input.needs_entertainment}

Additional requirements:
{budget_input.additional_requirements or "None"}

Return ONLY valid JSON.

Required structure:

{{
  "budget_breakdown": [
    {{
      "category": "Catering",
      "allocation": 3000,
      "items": [
        {{
          "name": "Food package",
          "description": "Description",
          "estimated_price": 200,
          "quantity": 10,
          "search_terms": "party catering"
        }}
      ]
    }}
  ],
  "additional_suggestions": [
    "Suggestion"
  ]
}}

Rules:

- Use INR.
- Keep total within the budget.
- Do not include alcohol.
- Do not include tobacco.
- Use practical Indian party planning assumptions.
- Prices are estimates.
"""

    result = _call(prompt)

    if not result:

        categories = []

        if budget_input.venue_type:

            categories.append({
                "category": "Venue",

                "items": [
                    {
                        "name":
                            "Community/event hall",

                        "description":
                            "Simple venue option",

                        "estimated_price":
                            max(
                                0,
                                min(
                                    budget_input.total_budget
                                    * 0.25,
                                    5000
                                )
                            ),

                        "quantity": 1,

                        "search_terms":
                            f"{budget_input.venue_type} event hall"
                    }
                ]
            })

        if budget_input.needs_catering:

            categories.append({
                "category": "Catering",

                "items": [
                    {
                        "name":
                            "Vegetarian meal package",

                        "description":
                            "Per-guest meal estimate",

                        "estimated_price":
                            max(
                                0,
                                min(
                                    (
                                        budget_input.total_budget
                                        * 0.35
                                        / max(
                                            1,
                                            budget_input.num_guests
                                        )
                                    ),
                                    350
                                )
                            ),

                        "quantity":
                            budget_input.num_guests,

                        "search_terms":
                            "vegetarian party catering"
                    }
                ]
            })

        if budget_input.needs_decoration:

            categories.append({
                "category": "Decoration",

                "items": [
                    {
                        "name":
                            "Basic balloon and backdrop set",

                        "description":
                            "Simple event decoration",

                        "estimated_price": 1500,

                        "quantity": 1,

                        "search_terms":
                            "party decoration backdrop balloons"
                    }
                ]
            })

        if budget_input.needs_entertainment:

            categories.append({
                "category": "Entertainment",

                "items": [
                    {
                        "name":
                            "Simple speaker and music setup",

                        "description":
                            "Basic event audio",

                        "estimated_price": 1500,

                        "quantity": 1,

                        "search_terms":
                            "party speaker rental"
                    }
                ]
            })

        result = {
            "budget_breakdown": categories,

            "additional_suggestions": [
                "Keep a small contingency reserve.",
                "Confirm guest count before finalizing catering."
            ]
        }

    return _finalize(
        result,
        "party",
        budget_input.total_budget,
        PARTY_PLATFORMS
    )


# =========================================================
# JEWELRY
# =========================================================

def jewelry(
    budget_input,
    image_bytes: bytes | None = None,
    mime_type: str | None = None
) -> dict[str, Any]:

    prompt = f"""
You are PocketSmart AI.

Create India-specific jewelry recommendations.

Budget:
{budget_input.total_budget}

Occasion:
{budget_input.occasion}

Style preferences:
{budget_input.preferences or "Not specified"}

If an outfit image is attached:

- Analyze only visible colors.
- Analyze broad outfit style.
- Analyze formality.
- Do not identify the person.
- Do not infer sensitive personal information.

Return ONLY valid JSON.

Required structure:

{{
  "outfit_analysis": {{
    "colors": ["color1", "color2"],
    "style": "style",
    "formality": "casual/formal/traditional"
  }},
  "budget_breakdown": [
    {{
      "category": "Jewelry",
      "allocation": 2500,
      "items": [
        {{
          "name": "Jewelry item",
          "description": "Description",
          "estimated_price": 1500,
          "quantity": 1,
          "search_terms": "search phrase"
        }}
      ]
    }}
  ],
  "styling_tips": [
    "Tip"
  ]
}}

Rules:

- Stay within budget.
- Use INR.
- Prices are estimates.
- Do not claim live stock.
- Do not claim exact current prices.
"""

    result = _call(
        prompt,
        image_bytes,
        mime_type
    )

    if not result:

        result = {
            "budget_breakdown": [

                {
                    "category": "Jewelry",

                    "items": [
                        {
                            "name":
                                "Elegant imitation necklace set",

                            "description":
                                "Occasion-friendly "
                                "necklace and earrings set",

                            "estimated_price": 1800,

                            "quantity": 1,

                            "search_terms":
                                "elegant necklace earrings set India"
                        },

                        {
                            "name":
                                "Minimal earrings",

                            "description":
                                "Simple matching earrings",

                            "estimated_price": 700,

                            "quantity": 1,

                            "search_terms":
                                "minimal earrings India"
                        }
                    ]
                }
            ],

            "styling_tips": [
                "Choose one statement piece and keep the rest simple."
            ]
        }

    return _finalize(
        result,
        "jewelry",
        budget_input.total_budget,
        JEWELRY_PLATFORMS
    )