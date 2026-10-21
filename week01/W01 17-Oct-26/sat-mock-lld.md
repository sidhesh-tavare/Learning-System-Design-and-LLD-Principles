# Week 1 · Sat (2026-10-17) · MOCK: LLD mock #1

**Time:** 120 min  ·  **Status:** ⬜ pending

## Goal
Close Friday's debt fast, then run your first timed machine-coding round on a small Week-1-level problem.
Done = 4 failing tests green, UML drawn from memory, and a scored `/lld-mock` (/25).

## Block 1 · Clear Friday's debt (30 min, hard stop) → `../W01 16-Oct-26/Code/solid_demo.py`
Only the 4 failing tests. Everything else on the pending list is **dropped** (hygiene gets graded in the mock anyway).
- [x] Repo **ABC** signature → `save(record: PlacedOrder)` in the base class (LSP)
- [x] Failure message shows the **attempted** amount, not Rs.0
- [x] `.quantize(Decimal("0.01"))` after the discount
- [x] `Order.items` → `tuple[Item, ...]`
- [ ] Rerun the tests: target **17/17**
- ⏱ At min 20 and not done? Stop coding, finish the next two items.

## Block 2 · Warm-up from memory (10 min, no notes, no looking at the code)
- [ ] Redraw the `solid_demo` UML in Mermaid → `uml_from_memory.md`, then compare arrow by arrow with `../W01 16-Oct-26/solid_demo_uml.md`
- [ ] Answer the 3 recall Qs below in writing

## Block 3 · LLD mock #1 (75 min, timed) → `mock01/`
- [ ] Run `/lld-mock tic-tac-toe`. Statement only, no hints for the first 15 min of being stuck (and a hint costs points)
- Flow: requirements + clarifying Qs (10) → entities + relationships (10) → Mermaid class diagram (10) → Python code + `main()` demo (40) → walkthrough (5)
- Things I'll grade hardest, from your weak spots:
  - **Data integrity:** is every stored field actually true at all times? (look at what happens on an invalid move)
  - **LSP:** no narrowed override signatures, no `NotImplementedError` stubs
  - **Hygiene:** no unused imports, no duplicate classes, every name means something
  - **Extensibility:** expect "what if the board is N×N / there are 3 players / the win rule changes?"

## Block 4 · Wrap (5 min)
- [ ] Note the score and your #1 miss in your own words

## Recall check (no notes, write answers here)
1. `PremiumPricing` adds a `min_order_value` check and raises if the order is below it. Which principle might that break, and why?
2. ABC vs `Protocol`: when do you pick `Protocol` in an LLD round, and what do you lose?
3. Your repo base class says `save(order: Order)` and the child says `save(record: PlacedOrder)`. Why is that an LSP violation even though the code runs?

**My answers:**
1.
2.
3.

## Next
- Sun: off
- Mon (Wk 2): `/weekly` first (confirm Mon–Thu of Week 1), then Creational patterns start
