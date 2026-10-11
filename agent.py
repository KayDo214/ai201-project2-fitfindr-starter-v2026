"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re
import config
import trace
from tools import suggest_outfit, create_fit_card
from mcp_client import call_tool
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    session = new_session(query, wardrobe)
    next_step = "parse_query"
    iteration = 0

    while True:
        iteration += 1
        trace.check_iterations(iteration)

        if next_step == "parse_query":
            price_match = re.search(
                r"\b(?:under|below|less\s+than|up\s+to|max(?:imum)?(?:\s+price)?(?:\s+of)?|budget(?:\s+of)?)"
                r"\s*\$?\s*(\d+(?:\.\d{1,2})?)",
                query,
                flags=re.IGNORECASE,
            )
            size_match = re.search(
                r"\bsize\s+([a-z0-9]+(?:[./-][a-z0-9]+)*)",
                query,
                flags=re.IGNORECASE,
            )

            description = query
            for match in (price_match, size_match):
                if match:
                    description = description.replace(match.group(0), " ")
            description = re.sub(
                r"^\s*(?:i(?:'m|\s+am)?\s+)?(?:looking|searching)(?:\s+for)?\s+",
                "",
                description,
                flags=re.IGNORECASE,
            )
            description = re.sub(r"\s+", " ", description).strip(" ,.-")

            session["parsed"] = {
                "description": description,
                "size": size_match.group(1).upper() if size_match else None,
                "max_price": float(price_match.group(1)) if price_match else None,
            }
            trace.step("parse_query", inputs=query, returned=str(session["parsed"]))
            next_step = "search_listings"

        elif next_step == "search_listings":
            results = call_tool("search_listings", {
                "description": session["parsed"]["description"],
                "size": session["parsed"]["size"],
                "max_price": session["parsed"]["max_price"],
            })
            session["search_results"] = results
            trace.step(
                "search_listings (via MCP)",
                inputs=str(session["parsed"]),
                returned=results,
                note=f"{len(results)} match(es)",
            )

            if not results:
                session["error"] = (
                    "No matching listings were found. Try a broader description, "
                    "another size, or a higher price limit."
                )
                trace.step(
                    "branch",
                    note="search returned []: stopping before suggest_outfit",
                )
                return session
            next_step = "select_item"

        elif next_step == "select_item":
            session["selected_item"] = session["search_results"][0]
            trace.step("select_item", returned=session["selected_item"])
            next_step = "suggest_outfit"

        elif next_step == "suggest_outfit":
            try:
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"], session["wardrobe"]
                )
            except ModelUnavailable as exc:
                session["error"] = (
                    "The outfit model is temporarily unavailable. Please try again later."
                )
                trace.step(
                    "suggest_outfit error",
                    inputs=session["selected_item"],
                    note=f"ModelUnavailable: {exc}",
                )
                return session

            trace.step(
                "suggest_outfit",
                inputs=session["selected_item"],
                returned=session["outfit_suggestion"],
            )
            next_step = "create_fit_card"

        elif next_step == "create_fit_card":
            try:
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"], session["selected_item"]
                )
            except ModelUnavailable as exc:
                session["error"] = (
                    "The fit-card model is temporarily unavailable. Please try again later."
                )
                trace.step(
                    "create_fit_card error",
                    inputs=session["selected_item"],
                    note=f"ModelUnavailable: {exc}",
                )
                return session

            trace.step(
                "create_fit_card",
                inputs=session["selected_item"],
                returned=session["fit_card"],
            )
            return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
