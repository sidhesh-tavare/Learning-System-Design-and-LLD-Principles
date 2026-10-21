# Mon 19 Oct 2026 · Wk 1 (catch-up) · LLD: Composition vs Inheritance
Time: ~60 min

## Goal
Know when to subclass and when to hold an object instead. This is the exact mistake from Sat's mock (`Player1`/`Player2`) and the only Wk 1 LLD topic still unchecked.

## Block 1 · Learn (20 min)
- [x] AlgoMaster LLD (https://algomaster.io/learn/lld/): `inheritance` → `composition` → `aggregation` → `association`. Optional: Head First Design Patterns Ch 1 (Strategy/duck example). Stop at "HAS-A vs IS-A"
- [x] Write 3 lines in your own words: (a) when IS-A is right, (b) 2 problems with deep inheritance, (c) how composition fixes them
- [x] Look at your `solid_demo.py`: find one place where you already used composition (hint: `OrderService` constructor)

## Block 2 · Build (30 min)
Task: **Employee class explosion**. A payroll app has `Manager`, `Engineer`, `ContractorManager`, `ContractorEngineer`, and HR wants `InternEngineer` + `PartTimeManager` next quarter. Each class computes `monthly_pay()` and `can_approve_leave()`.
- [x] Draw (paper or Mermaid) why this explodes: how many classes after 3 roles x 3 employment types?
- [x] Refactor in Python: ONE `Employee` dataclass that HAS-A role and HAS-A pay policy (ABC or Protocol each). Adding a new role/type must be a new class, zero edits to `Employee`
- [x] `main()` demo with 4 different employees; run it
- [x] Save as `week01/W01 19-Oct-26/employee_composition.py`

## Block 3 · Carried over (10 min, only if time)
- [ ] Tic-Tac-Toe: fix `winner=None` vs `Mark.Empty` check so `play()` runs, add `main()`, run once. Stop at "it runs". No polish

## Recall check (end, answer from memory, no peeking)
1. Give a one-line rule for choosing inheritance vs composition, with one example of each.
2. What is the "fragile base class" problem?
3. In Sat's mock, why were `Player1`/`Player2` subclasses wrong, and what should they have been?
