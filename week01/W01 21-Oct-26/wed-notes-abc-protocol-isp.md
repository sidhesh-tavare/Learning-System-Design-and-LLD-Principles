# Wed 21 Oct 2026 · Notes: ABC vs Protocol, ISP, UML

## Choosing ABC vs Protocol
| Question | Use |
|---|---|
| Do subclasses share real code or state (e.g. a fixed algorithm skeleton)? | **ABC** |
| Is it only a contract, with implementers living elsewhere (tests, third-party, other modules)? | **Protocol** |

- "Rigidity" or "important code" is not a reason. A Protocol plus `mypy` is just as strict.
- Protocol: the *consumer* defines the shape; implementers never import it. `FakeSink` and third-party classes fit without being edited. You can't make a third-party class inherit from your ABC.

## Nominal vs structural
- Nominal: counts only if you declare the lineage (`class X(Base)`). ABC.
- Structural: counts if the shape matches (method names/signatures). Protocol.

## `@runtime_checkable`
- `isinstance(x, Proto)` checks only that the method names exist, not argument types or return types.
- Signatures are checked by a static tool (`mypy`).
- `issubclass` doesn't work on Protocols that have data attributes.

## ISP
- No class should be forced to implement methods it doesn't use.
- Split by what each client needs. It is NOT "smaller and smaller" or one method per interface.
- Example: `ConsoleSink` only writes, so `read_all()` lives in a separate `ReadableSink`.

## Today's build: `report_exporter.py`
- Sinks = Protocols (`WritableSink`, `ReadableSink`). `ConsoleSink`/`FileSink`/`FakeSink` inherit nothing.
- `BaseFormatter` = ABC with template method: `format()` = validate → `_format_data()`. Subclasses override only `_format_data`.
- `ReportService` gets sink and formatter through its constructor (DIP).
- UML saved as `image.png`: realization arrows dashed + hollow triangle, inheritance solid + hollow triangle, `ReportService` → sink/formatter as associations.

## Mistakes / open items
- Said "rigidity" as the ABC reason (wrong criterion).
- `ReadableSink` is never used as a type, so the ISP split isn't demonstrated. Fix: `def count_reports(sink: ReadableSink) -> int` and call it on `FakeSink` in `main()`.
- `FileSink` appends to `reports.txt` every run, so `read_all()` mixes runs. Use a temp path or truncate at the start of the demo.
- Recall check (3 Qs) not done. Run it at the next `/recall`.

## One-liner
"ABC when subclasses share code, Protocol when it's only a contract and the implementers live elsewhere."
