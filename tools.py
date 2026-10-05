"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
import re
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

_STOPWORDS = {"a", "an", "and", "the", "for", "with", "under", "over", "in", "of"}

def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", " ", size or "")
    parts = [p.strip().upper() for p in cleaned.split("/")]
    return {p for p in parts if p}

def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()
    query_words = _keywords(description)

    scored_matches = []

    for listing in listings:
        # Price filter
        if max_price is not None and listing["price"] > max_price:
            continue

        # Size filter
        if size and not _size_matches(size, listing["size"]):
            continue

        # Build searchable text from useful listing fields
        searchable_parts = [
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            " ".join(listing.get("style_tags", [])),
            " ".join(listing.get("colors", [])),
            listing.get("brand") or "",
        ]

        listing_words = _keywords(" ".join(searchable_parts))

        # Number of query keywords found in listing
        score = len(query_words & listing_words)

        if score == 0:
            continue

        scored_matches.append((score, listing))

    # Best keyword overlap first
    scored_matches.sort(key=lambda pair: pair[0], reverse=True)

    return [
        listing
        for _, listing in scored_matches[:config.SEARCH_RESULT_LIMIT]
    ]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    items = wardrobe.get("items", [])

    if not items:
        prompt = f"""
    You are helping someone style a thrifted clothing item.

    New item:
    Title: {new_item.get("title")}
    Category: {new_item.get("category")}
    Colors: {", ".join(new_item.get("colors", []))}
    Style tags: {", ".join(new_item.get("style_tags", []))}

    The user has no wardrobe items available.

    Suggest one or two general ways they could style this item.
    Keep the answer concise and practical.
    """
    else:
        wardrobe_text = "\n".join(
            f"- {item.get('name')} | "
            f"category: {item.get('category')} | "
            f"colors: {', '.join(item.get('colors', []))} | "
            f"styles: {', '.join(item.get('style_tags', []))}"
            for item in items
        )

        prompt = f"""
    You are helping someone build an outfit around a thrifted item.

    New item:
    Title: {new_item.get("title")}
    Category: {new_item.get("category")}
    Colors: {", ".join(new_item.get("colors", []))}
    Style tags: {", ".join(new_item.get("style_tags", []))}

    The user's wardrobe:
    {wardrobe_text}

    Suggest one or two outfits using the new item together with specific pieces
    from the user's wardrobe. Name the wardrobe pieces you use.
    Keep the answer concise and practical.
    """

    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return "I couldn't create a fit card because no outfit suggestion was available."

    prompt = f"""
    Write a short social-media-style caption for this thrifted outfit.

    New item:
    Title: {new_item.get("title")}
    Price: ${new_item.get("price")}
    Platform: {new_item.get("platform")}
    Colors: {", ".join(new_item.get("colors", []))}
    Style tags: {", ".join(new_item.get("style_tags", []))}

    Outfit suggestion:
    {outfit}

    Requirements:
    - Write 2 to 4 sentences.
    - Mention the thrifted item.
    - Mention its price once.
    - Mention the platform once.
    - Describe the vibe of the outfit.
    - Make it sound like something a person might actually post.
    """

    return generate(prompt)

