# Session Notes · Fri 16 Oct 2026 · Week 1 · BUILD: SOLID Refactor

**Files:** `solid_demo.py` (the classes), `main.py` (demo runner), `fri-build-solid.md` (the plan)
**Review score:** 17/25 · **Status:** code runs; 4 review fixes applied after the review; 13/17 tests pass; rest pending (see the end)

---

## 1. What we set out to do

We refactored a **god class** into SOLID Python. The starting code:

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

class GiftCardPayment(CardPayment):
    def refund(self, amount): raise NotImplementedError("gift cards can't refund")
```

### What was wrong with it (one smell per principle)
| Smell | Principle broken | Who asks for the change (the actor) |
|---|---|---|
| Validation, pricing, payment, DB and email all in one method | **SRP** | Product, Finance, Payments team, DBA, Marketing: 5 reasons to change |
| `if/elif` on `customer_type` and `pay_method` strings | **OCP** | Adding "student" or "UPI" means editing this method |
| `GiftCardPayment.refund()` raises `NotImplementedError` | **LSP** | Code that calls `refund()` on any `CardPayment` crashes on a gift card |
| One fat payment interface with `pay` and `refund` | **ISP** | Gift card is forced to "implement" something it can't do |
| Hardcoded MySQL and email | **DIP** | High-level logic depends on low-level details; can't test without a DB |
| `dict` and `str` everywhere, `float` money | Typing/modelling | Typos aren't caught; `0.1 + 0.2 != 0.3` |

---

## 2. What we built, piece by piece

### 2.1 Data model: `Item` and `Order` (dataclasses)
```python
@dataclass(frozen=True)
class Item:
    name: str
    price: Decimal
    qty: int

@dataclass
class Order:
    items: list[Item]
    email: str

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("Items list cannot be empty")

    @property
    def subtotal(self) -> Decimal: ...
```
- **`Decimal` for money**, never `float`.
- **Validation lives in `Order.__post_init__`** (Information Expert: logic goes where the data is). An empty order can't even be created, so the illegal state can't be represented. We decided a separate `Validator` class would be YAGNI here: there's one rule and nothing to swap.
- **`subtotal` is a `@property`**: computed, read-only, and never stale.
- `Item` is `frozen=True` (a value object). `Order` is not frozen yet (see the pending fixes).

### 2.2 Pricing: Strategy pattern (OCP)
```python
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, subtotal: Decimal) -> Decimal: ...

class NoDiscount(DiscountStrategy): ...        # × 1.0
class PremiumDiscount(DiscountStrategy): ...   # × 0.9
class EmployeeDiscount(DiscountStrategy): ...  # × 0.7
```
- Each `if/elif` branch became **its own class behind one interface**. Adding a student discount means one new class and **zero edits** to existing code. That's OCP.
- We **dropped the `CustomerCategory` enum** from the core logic. With strategy classes, an enum would be a second place to edit (enum + class + mapping). An enum is fine only at the **boundary**: a string from the API or DB goes to a factory, which picks the strategy.

### 2.3 Payment: ABC + LSP/ISP fix
```python
class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount: Decimal) -> bool: ...

class CardPayment(PaymentMethod):    # pay + refund
class PayPalPayment(PaymentMethod):  # pay + refund
class GiftCardPayment(PaymentMethod):  # pay ONLY, with no fake refund()

class Refundable(Protocol):
    def refund(self, amount: Decimal) -> bool: ...
```
- **The LSP fix:** `GiftCardPayment` no longer inherits from `CardPayment`, so it no longer promises `refund()` and then breaks that promise.
- **The ISP fix:** "can pay" and "can refund" are **separate contracts**. `PaymentMethod` is the base ABC. `Refundable` is a capability Protocol that card and PayPal match structurally, without inheriting from it.
- **Why ABC for payment:** it's a family we own, and a subclass that forgets `pay()` fails at instantiation.
- **Why Protocol for `Refundable`:** it's a "can-do" capability. Any class with a matching `refund()` fits, including third-party classes, with no inheritance and no Adapter.
- **The payoff to be able to explain:** a future `refund(record, payment: Refundable)` will reject a `GiftCardPayment` at **type-check time**, before the code ever runs.

### 2.4 Persistence: Repository + DIP
```python
class OrderRepository(ABC):
    @abstractmethod
    def save(self, ...) -> None: ...

class InMemoryOrderRepository(OrderRepository):  # fake DB for main() and tests
```
- `OrderService` depends on the **abstraction**, never on MySQL. Swapping to Postgres means one new class.
- **Why ABC here:** we own the family of stores, and there is exactly one variant now, but it must be **swappable and fakeable**. That's the DIP reason to abstract (not OCP).

### 2.5 Notification: Protocol + DIP
```python
class Notifier(Protocol):
    def send(self, to: str, msg: str) -> None: ...

class ConsoleNotifier:   # note: no inheritance; it matches structurally
```
- **Why Protocol:** notifiers are often third-party SDK wrappers (SES, Twilio). Structural typing lets them fit with no inheritance.
- **The trade-off:** no runtime enforcement. Only mypy or the IDE catches a mismatch (`@runtime_checkable` is needed for `isinstance`).

### 2.6 `PlacedOrder` + `Status`: the bug fix of the day
```python
class Status(Enum):
    SUCCESS = 1
    FAILURE = 0

@dataclass(frozen=True)
class PlacedOrder:
    order: Order
    amount_paid: Decimal
    payment_method: PaymentMethod
    status: Status
```
**The bug:** the repo printed `order.subtotal` (222.0) as saved, but the customer was charged **199.80**. The DB recorded money that was never received.

**What we discussed:**
- Option A: add a mutable `final_amount: Decimal | None = None` to `Order`. It's the smallest change, but it allows an **invalid state**: an order with no total that someone can save anyway.
- Option B (chosen): a **separate frozen record** created *after* payment. It can't exist without a paid amount.
- **Core lesson: separate intent from outcome.** `Order` is what the customer asked for. `PlacedOrder` is what actually happened.
- **Why not recompute later?** Prices and discount rules change. If the premium discount moves from 10% to 15%, recomputing old orders rewrites history. **Record the amount charged at payment time.**
- Mistake along the way: `order.subtotal = total_amount`. That fails (a property with no setter raises `AttributeError`), and it's also wrong: "subtotal" means *before* discount, so overwriting it destroys data.

### 2.7 Orchestrator: `OrderService` (SRP + DIP)
```python
class OrderService:
    def __init__(self, repository: OrderRepository, notifier: Notifier) -> None: ...

    def place_order(self, order: Order, discount: DiscountStrategy,
                    payment: PaymentMethod) -> bool:
        # price → pay → build PlacedOrder → save → notify
```
- **It only orchestrates.** Each step is delegated to a collaborator.
- **Constructor injection** for long-lived dependencies (repo, notifier). **Per-call arguments** for things that vary per order (discount, payment).

### 2.8 `main.py`: the demo
Order A: premium discount + card → charged 199.80.
Order B: employee discount + gift card → charged 85.40. Both use `InMemoryOrderRepository`, with no DB.

---

## 3. Python toolkit used today
| Tool | Where we used it | Rule of thumb |
|---|---|---|
| `@dataclass` | `Item`, `Order`, `PlacedOrder` | Data holders; validate in `__post_init__` (exact name; `__post_init` is silently never called) |
| `frozen=True` | `Item`, `PlacedOrder` | Value objects and records. **Shallow**: mutable contents inside can still change |
| `@property` | `Order.subtotal` | Derived values that must never go stale; read-only unless you add a setter |
| `ABC` | `DiscountStrategy`, `PaymentMethod`, `OrderRepository` | A family you own; enforced at instantiation |
| `Protocol` | `Refundable`, `Notifier` | Capabilities; foreign classes fit without inheriting; checked by mypy only |
| `Enum` | `Status` | Fixed tags; use `auto()` and meaningful names |
| `Decimal` | All money | Never `float`; round with `.quantize(Decimal("0.01"))` |

**Dataclass gotcha we hit:** a field with a default can't come before a field without one.

---

## 4. `/review` result: 17/25

| Area | Score |
|---|---|
| Requirements | 4 |
| Class design | 3 |
| Patterns | 4 |
| Code quality | 2 |
| Extensibility | 4 |

### Bugs found
1. **The repo still drops the paid amount.** `self.orders.append(order.order)` stores the `Order`, not the `PlacedOrder`. Only the *print* was fixed. **Check what is stored, not what is shown.**
2. **LSP on signatures.** Base `save(order: Order)` vs child `save(order: PlacedOrder)`: an override can't accept a *narrower* parameter type. Fix the abstraction itself.
3. **`PlacedOrder` defined twice** (lines 104 and 138); the second silently replaces the first.
4. **A failure record claims a payment.** `amount_paid=total_amount` with `status=FAILURE`. It's also built and then thrown away.

### Design issues
- `Status.SUCCESS/FAILURE = 1/0`: a vague name and magic numbers. Better: `OrderStatus.PLACED / PAYMENT_FAILED` with `auto()`.
- `pay() -> bool` can't say *why* a payment failed; `== False` should be `if not ok`.
- `PlacedOrder` stores a **service object** (`CardPayment()`) instead of data, such as a `PaymentType` enum.
- `frozen=True` is shallow: `Order.items` is a mutable list, so use `tuple[Item, ...]`.
- No money rounding after a percentage discount.
- `place_order` returns `bool`; returning the `PlacedOrder` would be more useful and testable.
- `main()` only tests the happy path; `PayPalPayment` and `NoDiscount` are never run.

### Hygiene
Unused imports (`field`, `Dict`, `Any`, `Optional`), wrong indentation at line 88, nested `"` in the f-string at line 135 (only works on 3.12+), "proesssed" typo, `from solid_demo import *`, PascalCase variable `OrderA`.

### Extensibility scorecard
| Change request | Edits to existing code? |
|---|---|
| Add UPI payment | ✅ none, one new class |
| Add student discount | ✅ none |
| SMS instead of email | ✅ none |
| Swap to Postgres | ✅ none |
| Premium **plus** a festival coupon | ❌ only one strategy fits; comes back in the Week 2–3 patterns |

---

## 4b. After the review: fixes applied + test run (16 Oct, ~11:30)

### Fixed ✅
| Review finding | What changed |
|---|---|
| Duplicate `PlacedOrder` | Removed; only one definition now (line 104) |
| Repo dropped the paid amount | `InMemoryOrderRepository` now stores `list[PlacedOrder]` and appends the full record |
| `amount_paid` set on a failed payment | Failure record now uses `Decimal("0")` |
| Magic-number enum | `Status` now uses `auto()` |
| Couldn't see stored data | `main()` prints `curr_db.orders` to show what is actually stored |

`python main.py` output: Order A 199.80 (premium + card), Order B 85.40 (employee + gift card). Both are stored as `PlacedOrder(status=SUCCESS)` with the correct `amount_paid`. ✅

### Test run: 17 tests with `unittest`, 13 pass, 4 fail
Claude wrote these tests in a scratch file (not in your folder), using `FakeNotifier` (captures messages) and `FailingPayment` (`pay()` → False) as test doubles. That injection is only possible because of DIP.

**Passing (13):** what your design gets right
| Area | Test |
|---|---|
| Model | `subtotal` = 222.0 · empty order → `ValueError` · `Item` is frozen · `subtotal` has no setter |
| Strategy / OCP | all 3 discounts compute correctly · a **new `StudentDiscount` works with zero edits** (charged 177.60) |
| ABC | a `PaymentMethod` subclass without `pay()` can't be instantiated (`TypeError`) |
| LSP / ISP | `GiftCardPayment` has no `refund`; Card and PayPal do |
| Service | premium + card stores **199.80** with SUCCESS (the bug from today stays fixed) · PayPal + no discount stores 222.0 · failed payment returns `False`, **saves nothing**, still notifies the customer · `PlacedOrder` is frozen · `ConsoleNotifier` runs |

**Failing (4):** known issues; each test asserts the behaviour the review asked for
| Test | Actual result | Why it matters |
|---|---|---|
| Failure message shows the attempted amount | Message says "Order of **Rs.0** not confirmed" | You use `placed_order.amount_paid` (0) in the message; the customer needs the amount that was *attempted* (199.80). The 0 is right in the record but wrong in the message |
| Money rounded to 2 decimal places | Item at 33.33 with premium discount → charged **29.997** | No `.quantize(Decimal("0.01"))`; you can't charge a third of a paisa |
| `PlacedOrder` deeply immutable | `rec.order.items.append(...)` **succeeds** | `frozen=True` is shallow; a stored record can be changed after the fact |
| Repo ABC signature matches the child | Base `save(order: Order)` ≠ child `save(order: PlacedOrder)` | LSP violation: the abstraction still promises to accept an `Order` |

### Design decision now in the code
On payment failure **nothing is saved**, and the `PlacedOrder` is built only to make the message. That's defensible ("only successful orders are orders"), but then building the record is pointless. Real systems usually log failed attempts for audit and fraud checks. Pick one and be ready to defend it in the mock.

---

## 5. Interview one-liners from today
- **SRP:** "One reason to change means one *actor* who requests edits. Name who asks."
- **OCP:** "If I see `if/elif` on a type, each branch becomes a class behind one interface."
- **LSP:** "A subclass that raises `NotImplementedError` or narrows its input types isn't substitutable."
- **ISP:** "Split 'can pay' from 'can refund' so a gift card isn't forced to fake a refund."
- **DIP:** "The service depends on `OrderRepository`, not MySQL. That's why I can test with an in-memory fake."
- **Records:** "I separate intent (`Order`) from outcome (`PlacedOrder`) and record the charged amount at payment time, because pricing rules change."
- **Before saving anything, ask: is every field in this record actually true?**

## 6. My mistakes today (don't repeat)
- Treated a runtime input as a "reason to change" (SRP is about code edits that someone requests).
- Wrote `__post_init` without the trailing `__`.
- Put a defaulted dataclass field before a non-defaulted one.
- Needed "show solution" for the Protocol/ISP split.
- Tried `order.subtotal = total_amount` (a property has no setter, and it overwrites the meaning).
- Fixed the print but not the storage; recorded `amount_paid` on a failed payment.
- Narrowed a parameter type in an override (LSP).
- Left a duplicate class definition and unused imports.

---

## 7. Still pending (carry to Sat before the mock)
- [x] Repo stores `PlacedOrder`
- [ ] Repo **ABC** signature: `save(record: PlacedOrder)` in the base class too (test 4 failing)
- [x] Delete the duplicate `PlacedOrder`
- [x] `Status` uses `auto()`
- [ ] Rename `Status` → `OrderStatus` (`PLACED` / `PAYMENT_FAILED`)
- [x] On failure, `amount_paid = 0`
- [ ] Failure message shows the attempted amount, not Rs.0 (test 1 failing)
- [ ] Decide: save failed attempts or not; if not, don't build the record
- [ ] `.quantize(Decimal("0.01"))` after discount (test 2 failing)
- [ ] `Order.items` → `tuple[Item, ...]` for real immutability (test 3 failing)
- [ ] `place_order` returns `PlacedOrder` instead of `bool`
- [ ] Record a payment type (enum) instead of the service object, without an `if/elif`
- [ ] `main()`: add a `FailingPayment` fake and use `PayPalPayment` and `NoDiscount`
- [ ] One-line principle comment above every class
- [ ] Hygiene: unused imports, indentation at line 88, f-string quotes at line 135, "proesssed", star import, stale comment at line 16
- [x] `solid_demo_uml.md`: Mermaid class diagram (drawn by Claude on request)
- [ ] Sat: redraw the UML **from memory** in 10 min and compare arrow by arrow (UML drawing is still untested)
- [ ] Answer the 3 recall questions in `fri-build-solid.md` with no notes
- [ ] Stretch: write your own `test_solid_demo.py` with `unittest` (fakes for the notifier and payment); target 17/17 green
