# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is an agent that helps a user find a thrifted clothing item and build an outfit around it. The user provides a natural-language request such as a vintage graphic tee under a certain price. The agent searches the available listings, selects a matching item, suggests an outfit using the user's wardrobe, and creates a short fit-card caption. If no listing matches, the agent stops early and tells the user what they can change in the search.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

**What it does:** Searches the available clothing listings for items matching the requested description, size, and maximum price.

**Inputs:**
- `description` (`str`) — what kind of item the user wants
- `size` (`str`) — requested clothing size
- `max_price` (`float`) — highest price the user is willing to pay

**Returns:** A `list` of listing dictionaries. Each listing includes fields such as `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

**When it has nothing:** Returns an empty list `[]`.

### `suggest_outfit`

**What it does:** Suggests an outfit using the newly found item together with items from the user's wardrobe.
**Inputs:**
- `new_item` (`dict`) — the selected listing returned by `search_listings`
- `wardrobe` (`dict`) — a wardrobe dictionary whose `items` key contains the user's existing wardrobe items
**Returns:** 
A `str` containing an outfit suggestion that combines the new item with suitable wardrobe items.

**When it has nothing:** 
Returns a general outfit suggestion based on the new item instead of failing.

### `create_fit_card`

**What it does:** Creates a short caption describing the outfit and the newly selected item.

**Inputs:**
- `outfit` (`str`) — the outfit suggestion produced by `suggest_outfit`
- `new_item` (`dict`) — the selected listing

**Returns:**
A `str` containing a short fit-card caption that someone could realistically post.

**If required input is missing:**
Returns a clear error message instead of crashing.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, the agent stores a message explaining that no listing matched and stops. Otherwise, it selects the first listing, stores it in the session, and continues to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** The query is parsed with regular expressions. The loop extracts a price from phrases such as `under $30` and a size from phrases such as `size M`. Those parts are removed from the original query, and the remaining text becomes the item description.

**What moves through the session:** The parsed description, size, and maximum price are stored in `session["parsed"]`. Search results go into `session["search_results"]`, the first result becomes `session["selected_item"]`, the outfit result goes into `session["outfit_suggestion"]`, and the final caption goes into `session["fit_card"]`. If search returns no results, `session["error"]` is set and the loop stops.

---

## Sample Run

**One full query**

```text
$ python agent.py

=== A query the data can match ===
  found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
  outfit:   Here is a fun, balanced outfit using your new Y2K butterfly baby tee:

**Outfit: Streetwear Y2K Contrast**
*   **Top:** Y2K Butterfly Baby Tee (New item)
*   **Bottoms:** Baggy straight-leg jeans (dark wash)
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag

**Why it works:** The fitted silhouette of the baby tee balances out the relaxed,
baggy fit of the dark wash jeans for a classic Y2K proportions play. Throwing on
the black denim jacket and chunky white sneakers keeps the streetwear vibe cohesive
while letting the pink and purple butterfly print pop.

  fit card: Mastering that classic Y2K proportion play is so easy when you style
this thrifted butterfly baby teewith some baggy dark wash denim. I threw on a black
jacket and chunky sneakers to complete the streetwear vibe while letting those pink
and purple graphics pop. Grab this little tee on my Depop right now for just $18! 🦋✨

=== A query it can't ===
  stopped: No matching listings were found. Try a broader description, another
  size, or a higher price limit.
  fit_card is None — it should still be None here

The second one should stop before the fit card. If both paths look the same,
the branch isn't doing anything yet.

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```text
$ python -c "from tools import search_listings; print(search_listings('graphic tee', size='L', max_price=30))"

[
  {
    'id': 'lst_006',
    'title': 'Graphic Tee — 2003 Tour Bootleg Style',
    'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.',
    'category': 'tops',
    'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'],
    'size': 'L',
    'condition': 'good',
    'price': 24.0,
    'colors': ['black'],
    'brand': None,
    'platform': 'depop'
  },
  {
    'id': 'lst_033',
    'title': 'Vintage Band Tee — Faded Grey',
    'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.',
    'category': 'tops',
    'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'],
    'size': 'L',
    'condition': 'fair',
    'price': 19.0,
    'colors': ['grey', 'charcoal'],
    'brand': None,
    'platform': 'depop'
  },
  {
    'id': 'lst_015',
    'title': 'Vintage Graphic Hoodie — Faded Black',
    'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.',
    'category': 'tops',
    'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'],
    'size': 'L',
    'condition': 'fair',
    'price': 26.0,
    'colors': ['black', 'charcoal'],
    'brand': None,
    'platform': 'depop'
  }
]
```
$ python -c "from tools import suggest_outfit; ..."

```
Scored these vintage Levi's 501s for just $38 on Depop and I'm obsessed!
Throwing them on with some fresh white sneakers gives off the ultimate effortless
streetwear vibe. Grab them before I change my mind and keep them all to myself! ✨👖
```
$ python -c "from tools import create_fit_card; ..."
```text
Here are two ways to style your new Vintage Levi's 501 Jeans using items from your wardrobe:

**Outfit 1: Casual Streetwear**
*   **Top:** White ribbed tank top (tucked in)
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   *Why it works:* The fitted white tank balances the classic straight-leg fit of the 501s, while the black denim jacket and chunky sneakers lean into an effortless, vintage-meets-streetwear aesthetic.

**Outfit 2: Cozy & Classic**
*   **Top:** Oversized grey crewneck sweatshirt 
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt
*   *Why it works:* Tucking the medium wash denim into the brown belt adds definition, paired with the oversized grey crewneck and combat boots for a grunge-leaning, comfortable everyday look.
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked AI to explain the difference between a normal pipeline and an agent planning loop, and how session state works in this project.
- *What came back:* It explained that the important difference is the branch after `search_listings`, and that results should move through the session so later tools can use them.
- *What I changed:* I used that explanation to write my Planning Loop section and to understand why the selected item, outfit suggestion, and fit card should each be stored in the session.

**Moment 2**

- *What I asked for:* I used AI to help implement the planning loop in `agent.py`.
- *What came back:* It suggested using a `next_step` variable inside a `while` loop, with states for parsing, search, item selection, outfit generation, and fit-card generation.
- *What I changed:* I kept that structure and verified that the no-results branch returns immediately before `suggest_outfit`, while a successful search continues through the remaining tools.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

I ran all five acceptance criteria five times each with caching disabled using:

```bash
python run_eval.py --label before
```

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools and returns a fit card | At least 4/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 2. Impossible query stops before `suggest_outfit` and returns a useful message | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 3. Selected item stays consistent when passed into `suggest_outfit` | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 4. Fit card refers to the selected item and describes the outfit | At least 4/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 5. Search results respect requested size and maximum price | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |

**Real output from one try**, pasted as text, naming the file and function
that produced it: 

Produced by `agent.py::run_agent` and recorded by `run_eval.py`.

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}

[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)

[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)

[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)

[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)

try 1: completed — fit card 296 chars
```

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools and returns a fit card | At least 4/5 | MET — 5/5 | All five runs reached `suggest_outfit` and `create_fit_card` and produced a non-empty fit card. |
| 2 | Impossible query stops before `suggest_outfit` and returns a useful message | 5/5 | MET — 5/5 | All five runs returned an empty search result, took the early-stop branch, and did not call `suggest_outfit`. |
| 3 | Selected item stays consistent when passed into `suggest_outfit` | 5/5 | MET — 5/5 | In every run, the item shown by `select_item` was the same item shown as the input to `suggest_outfit`. |
| 4 | Fit card refers to the selected item and describes the outfit | At least 4/5 | MET — 5/5 | All five fit cards referred to the selected item and included styling or outfit information. |
| 5 | Search results respect requested size and maximum price | 5/5 | MET — 5/5 | The query was consistently parsed as size `L` with a maximum price of `$30`, and the returned results stayed within those constraints. |

**Diagnoses**

None of the five acceptance criteria missed their original targets, so there was no required miss diagnosis.

However, the evaluation exposed a search-quality weakness that is not captured by the current criteria. For the query `denim jacket under $50`, `search_listings` returned loosely related results such as jeans and other kinds of jackets. The likely mechanism is the keyword-overlap scoring in `tools.py`: a listing can be accepted when it shares only one keyword with the query. For example, jeans may match on `denim`, while a track jacket may match on `jacket`.

This does not violate the current acceptance criteria, but it is a good candidate for the measured improvement.

---

## Loop Trace

     

**Happy path**

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}

[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)

[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)

[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)

[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
```

**Empty search**

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}

[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    0 match(es)

[3] branch
      →    search returned []: stopping before suggest_outfit
```

**On the MCP move:**

Before the rewire, `agent.py` called `tools.py::search_listings` directly. After the change, `agent.py` calls `mcp_client.call_tool("search_listings", ...)`, which sends the request through `mcp_server.py`.

`mcp_server.py` exposes `search_listings` as an MCP tool and forwards the inputs to the original implementation in `tools.py`. The returned data still has the same list-of-dictionaries structure, so the rest of the planning loop did not need to change.

The main visible difference is that the trace now shows `search_listings (via MCP)`.

### Failure-mode checks

I deliberately tested three failure modes:

1. **Empty search result:** an impossible query returned `[]`, so the agent stopped before `suggest_outfit`.
2. **Empty wardrobe:** `suggest_outfit` received no wardrobe items and returned general styling advice instead of crashing.
3. **Model unavailable:** I forced a model-backed tool to raise `ModelUnavailable`. The agent caught it, stored a readable error in the session, recorded the failure in the trace, and returned without crashing.

---

## The Improvement

**What I changed:**

I tightened the keyword matching in `tools.py::search_listings`. Previously, any listing with at least one overlapping keyword could be included. After the change, queries with two or more keywords require at least two keyword matches.

**Which failure it was meant to fix:**

The before-run exposed a search-quality weakness. The query `denim jacket under $50` returned loosely related items such as jeans and other jackets because matching only `denim` or only `jacket` was enough to keep a result.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools and returns a fit card | At least 4/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 2. Impossible query stops before `suggest_outfit` and returns a useful message | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 3. Selected item stays consistent when passed into `suggest_outfit` | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 4. Fit card refers to the selected item and describes the outfit | At least 4/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 5. Search results respect requested size and maximum price | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |

**Did it help, and how do I know:**

Yes. Before the change, the query `denim jacket under $50` returned 7 results, including loosely related items such as jeans and other jackets.

After the change, the same query consistently returned only one result: `Denim Jacket — Light Wash, Cropped`.

The original five acceptance criteria still passed after the change, so the stricter matching improved search relevance without breaking the existing behavior.

---

## What's Still Broken

All five acceptance criteria passed after the improvement.

Search relevance is still based on simple keyword overlap, so it is not a true semantic search. A listing can still match because relevant words appear in style tags or descriptions even when the exact item category is not a perfect match.

For this unit, I stopped after improving the most obvious partial-match problem and verifying that the original criteria still passed. A future improvement could use category-aware scoring or semantic similarity for better ranking.

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
