# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
I chose 4 of 5 instead of 5 of 5 because the agent uses model-based tools (usually, function that calls an AI model) for outfit generations and fit_card generation so the output can vary. Despite the variation, a matching query should still complete the full workflow most of the time.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
I chose 5 of 5 because this behavior is controlled by the planning loop, not by a model-generated response. If `search_listings` returns no matches, the agent should always stop before calling `suggest_outfit` and tell the user what they could change in their search.

---

## 3. Something about state

Given a successful search, the listing stored in
`session["selected_item"]` has the same `id` as the `new_item`
passed to `suggest_outfit` — 5 of 5 tries.

**Why this target:**
I chose 5 of 5 because session state is deterministic program logic.
The same selected listing should always be passed to the next tool.

---

## 4. The fit card includes the selected item

Given a successful run, the fit card refers to the selected item and
describes the outfit in a short, readable caption — in at least 4 of 5 tries.

**Why this target:**
I chose 4 of 5 because `create_fit_card` uses a language model, so its
wording can vary between runs. The exact wording does not need to match,
but the result should still clearly describe the selected item and outfit.

---

## 5. Search results respect the user's constraints

Given a query that returns at least one listing, the selected listing
must be at or below the requested maximum price and match the requested
size — 5 of 5 tries.

**Why this target:**
I chose 5 of 5 because price and size filtering are handled by normal
program logic rather than model generation, so these constraints should
be applied consistently.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
