# Wed 21 Oct 2026 · Wk 1 · LLD: ABC vs Protocol + UML retest
Time: ~60 min

## Goal
Know which of ABC / Protocol to reach for and why, then prove your UML arrows stick. This closes two open Wk 1 items: Protocol/ISP (needed "show solution" on 16 Oct) and UML (paper redraw only 🟡).

## Heads-up
Tue 20 Oct estimation has no record, so it slipped. It moves to Sat 24 Oct (30 min before the light HLD mock). Do not skip it again: estimation is on the critical path for every HLD mock.

## Block 1 · Learn (15 min)
- [x] AlgoMaster LLD (https://algomaster.io/learn/lld/): `interfaces` → `abstraction`. Recheck `isp` (your weak spot)
- [x] Python docs: `abc.ABC` vs `typing.Protocol` (nominal vs structural typing). Skim only
- [x] Write 3 lines in your own words: (a) when ABC, (b) when Protocol, (c) what "structural typing" means

## Block 2 · Build (30 min)
Task: **Report exporter**. A `ReportService` builds a report (list of rows) and sends it somewhere.
- [ ] Sinks: `ConsoleSink`, `FileSink`, plus a `FakeSink` for tests. `ReportService` must not import any concrete sink. Decide ABC or Protocol for the sink type and put a 1-line comment saying why
- [ ] Formatters: `CsvFormatter`, `JsonFormatter`. They share a fixed skeleton (validate rows → format → return string) and differ in one step. Decide ABC or Protocol and comment why
- [ ] ISP check: add a `ReadableSink` capability (`read_all()`) that only `FileSink` and `FakeSink` support. `ConsoleSink` must not be forced to implement it
- [ ] One class that satisfies your sink Protocol WITHOUT inheriting from anything (the point of Protocol)
- [ ] `main()` demo, run it, then run `mypy` if installed (optional, 2 min)
- [ ] Save as `week01/W01 21-Oct-26/report_exporter.py`

## Block 3 · UML retest (10 min)
- [ ] Close the code. On paper, draw the class diagram of `report_exporter.py` from memory with correct arrows (realization, inheritance, dependency, composition/aggregation where they apply). Then compare with the code and fix wrong arrows
- [ ] Photo or Mermaid copy into this folder

## Block 4 · Only if time left (5 min)
- [ ] Tic-Tac-Toe: fix `winner=None` vs `Mark.Empty` so `play()` runs. Stop at "it runs"

## Recall check (end, from memory, no peeking)
1. ABC vs Protocol: one rule for choosing, one example of each from today's code.
2. What does the ISP split buy you, in terms of `ConsoleSink`?
3. Which arrow is realization, and which is dependency? Name the line style and arrowhead for each.
