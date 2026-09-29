from urllib.parse import quote_plus


# =========================================================
# Platform search URLs
# =========================================================

PLATFORMS = {
    "Amazon": "https://www.amazon.in/s?k={query}",
    "Flipkart": "https://www.flipkart.com/search?q={query}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={query}",
    "Swiggy": "https://www.swiggy.com/search?query={query}",
    "Zomato": "https://www.zomato.com/search?query={query}",
    "OYO": "https://www.oyorooms.com/search?location={query}",
}


def make_search_url(
    platform: str,
    query: str,
) -> str:

    template = PLATFORMS.get(
        platform,
        PLATFORMS["Amazon"],
    )

    return template.format(
        query=quote_plus(query)
    )


def platform_for_category(
    planner: str,
    category: str,
) -> str:

    if planner == "home":

        if category.lower() in {
            "furniture",
            "storage",
            "lighting",
        }:
            return "IKEA"

        return "Amazon"

    if planner == "party":

        if category.lower() == "food":
            return "Swiggy"

        if category.lower() == "venue":
            return "OYO"

        return "Amazon"

    if planner == "jewelry":
        return "Amazon"

    return "Amazon"


def enrich_item(
    planner: str,
    category: str,
    name: str,
    estimated_price: float,
    reason: str,
) -> dict:

    platform = platform_for_category(
        planner,
        category,
    )

    return {
        "category": category,
        "name": name,
        "estimated_price": round(
            float(estimated_price),
            2,
        ),
        "reason": reason,
        "platform": platform,
        "search_url": make_search_url(
            platform,
            name,
        ),
    }
