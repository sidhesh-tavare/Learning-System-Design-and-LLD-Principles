# Week 1 · Fri (2026-10-16) · BUILD: SOLID refactor

**Time:** 60 min  ·  **Status:** 🟡 Code done + reviewed (17/25). UML, recall Qs and fixes carried to Sat. Notes: [session-notes-solid-refactor.md](session-notes-solid-refactor.md)

## Goal
Refactor a god-class into SOLID Python (ABC, Protocol, dataclass, Enum, constructor injection), then draw the UML.
Done = you can point at your own code and explain each principle.

## 1. Watch (15 min, skip if you already covered SOLID Mon/Wed)
- [ ] Concept && Coding — "SOLID Principles" (LLD playlist), 1.5–2x. Focus on **O, L, D**.
- Alex Xu doesn't cover LLD, so there's no chapter for this.

## 2. Build (35 min) → `week01/solid_demo.py`

Starting code (bad on purpose, you're refactoring it):

```python
class OrderService:
    def process(self, order: dict, customer_type: str, pay_method: str) -> None:
        if not order["items"]:
            raise ValueError("empty")
        total = sum(i["price"] * i["qty"] for i in order["items"])
        if customer_type == "regular":   total *= 1.0
        elif customer_type == "premium": total *= 0.9
        elif customer_type == "employee": total *= 0.7
        if pay_method == "card":   print(f"Charging card {total}")
        elif pay_method == "paypal": print(f"PayPal {total}")
        print(f"INSERT INTO orders ... {total}")          # MySQL hardcoded
        print(f"Emailing {order['email']}: order placed")  # email hardcoded

class GiftCardPayment(CardPayment):  # assume CardPayment has pay() and refund()
    def refund(self, amount): raise NotImplementedError("gift cards can't refund")
```

### Acceptance criteria
- [x] **OCP:** adding UPI payment or a "student" discount needs **zero edits** to existing classes
- [x] **SRP:** `OrderService` only orchestrates. Validation, pricing, payment, persistence and notification each get their own class
- [x] **DIP:** dependencies are injected via `__init__`. `ABC` for payment and repository, `Protocol` for the notifier. Be able to say *why* each
- [x] **LSP/ISP:** fix `GiftCardPayment` properly (raising `NotImplementedError` doesn't count as a fix)
- [ ] `@dataclass` for `Order`/`Item`, and an `Enum` wherever a string was a type tag
- [x] `main()` runs 2 orders with different payment/discount combos, using a `FakeRepository` (no DB)
- [ ] One-line comment above each class naming the principle it serves

## 3. UML (10 min) → `week01/solid_demo_uml.md`
- [ ] Mermaid class diagram with inheritance, interface realization and composition, each arrow used correctly
- ⏱ Not done by min 45? Drop the UML, finish the code, and do the UML Saturday before the mock.

## 4. Recall check (no notes, write your answers below)
1. `PremiumPricing` adds a `min_order_value` check and raises if the order is below it. Which principle might that break, and why?
2. ABC vs `Protocol`: when do you pick `Protocol` in an LLD round, and what do you lose?
3. "DIP just means using dependency injection." What's wrong with that?

**My answers:**
1.
2.
3.

## Next
- [x] Run `/review` on `solid_demo.py` (17/25)
- Sat: first **LLD mock** (small Week 1 problem)
