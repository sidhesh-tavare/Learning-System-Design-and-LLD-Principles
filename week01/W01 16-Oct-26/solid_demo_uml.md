# UML: solid_demo.py (Week 1 Fri)

Drawn by Claude from the code **as it stands on 16 Oct** (known issues included and marked ⚠).
**Sat task:** close this file and redraw it from memory in 10 min, then compare arrow by arrow.

## Class diagram
```mermaid
classDiagram
    direction TB

    %% ---------- Data ----------
    class Item {
        <<frozen dataclass>>
        +name: str
        +price: Decimal
        +qty: int
    }
    class Order {
        <<dataclass>>
        +items: list~Item~
        +email: str
        +subtotal: Decimal  «property»
        -__post_init__() None
    }
    class Status {
        <<enumeration>>
        SUCCESS
        FAILURE
    }
    class PlacedOrder {
        <<frozen dataclass>>
        +order: Order
        +amount_paid: Decimal
        +payment_method: PaymentMethod
        +status: Status
    }

    %% ---------- Pricing (Strategy / OCP) ----------
    class DiscountStrategy {
        <<abstract>>
        +apply(subtotal: Decimal) Decimal*
    }
    class NoDiscount
    class PremiumDiscount
    class EmployeeDiscount

    %% ---------- Payment (LSP / ISP) ----------
    class PaymentMethod {
        <<abstract>>
        +pay(amount: Decimal) bool*
    }
    class Refundable {
        <<protocol>>
        +refund(amount: Decimal) bool
    }
    class CardPayment {
        +pay(amount: Decimal) bool
        +refund(amount: Decimal) bool
    }
    class PayPalPayment {
        +pay(amount: Decimal) bool
        +refund(amount: Decimal) bool
    }
    class GiftCardPayment {
        +pay(amount: Decimal) bool
    }

    %% ---------- Persistence (DIP) ----------
    class OrderRepository {
        <<abstract>>
        +save(order: Order) None*
    }
    class InMemoryOrderRepository {
        +orders: list~PlacedOrder~
        +save(order: PlacedOrder) None
    }

    %% ---------- Notification (DIP) ----------
    class Notifier {
        <<protocol>>
        +send(to: str, msg: str) None
    }
    class ConsoleNotifier {
        +send(to: str, msg: str) None
    }

    %% ---------- Orchestrator (SRP) ----------
    class OrderService {
        -repository: OrderRepository
        -notifier: Notifier
        +place_order(order, discount, payment) bool
    }

    %% Inheritance (is-a)
    DiscountStrategy <|-- NoDiscount
    DiscountStrategy <|-- PremiumDiscount
    DiscountStrategy <|-- EmployeeDiscount
    PaymentMethod <|-- CardPayment
    PaymentMethod <|-- PayPalPayment
    PaymentMethod <|-- GiftCardPayment
    OrderRepository <|-- InMemoryOrderRepository

    %% Realization (structural, no inheritance in the code)
    Refundable <|.. CardPayment
    Refundable <|.. PayPalPayment
    Notifier <|.. ConsoleNotifier

    %% Composition / aggregation / association
    Order "1" *-- "1..*" Item : items
    PlacedOrder --> Order
    PlacedOrder --> PaymentMethod
    PlacedOrder --> Status
    InMemoryOrderRepository "1" o-- "*" PlacedOrder : stores
    OrderService o-- OrderRepository : injected
    OrderService o-- Notifier : injected

    %% Dependency (method parameters / creates)
    OrderService ..> DiscountStrategy : per call
    OrderService ..> PaymentMethod : per call
    OrderService ..> Order : per call
    OrderService ..> PlacedOrder : creates
```

## Why each arrow
| Relationship | Arrow | Reason |
|---|---|---|
| `NoDiscount` / `Premium` / `Employee` → `DiscountStrategy` | `<\|--` inheritance | They subclass the ABC |
| `Card` / `PayPal` / `GiftCard` → `PaymentMethod` | `<\|--` inheritance | They subclass the ABC |
| `Card`, `PayPal` → `Refundable` | `<\|..` realization | A Protocol is matched **structurally**; there's no inheritance in the code, so it gets a dashed line |
| `GiftCardPayment` → `Refundable` | **no arrow** | This is the ISP fix: gift cards make no refund promise |
| `ConsoleNotifier` → `Notifier` | `<\|..` realization | Same reason: a Protocol, not inherited |
| `OrderService` → repo, notifier | `o--` aggregation | **Injected** from outside via `__init__`; they outlive the service and can be shared. If the service created them itself, it would be composition (and break DIP) |
| `OrderService` → discount, payment, order | `..>` dependency | Only **method parameters**, never stored as fields |
| `OrderService` → `PlacedOrder` | `..>` dependency «creates» | It builds the record but doesn't keep it |
| `Order` → `Item` | `*--` composition, `1..*` | Items belong to the order, and `__post_init__` enforces at least 1 |
| `PlacedOrder` → `Order` / `Status` / `PaymentMethod` | `-->` association | Fields that reference other objects |
| `InMemoryOrderRepository` → `PlacedOrder` | `o--` aggregation, `*` | The repo stores records it didn't create |

## ⚠ Problems the diagram makes visible
1. **`OrderRepository.save(order: Order)` vs `InMemoryOrderRepository.save(order: PlacedOrder)`:** the signatures differ on the two boxes of an inheritance arrow. That's the LSP violation (failing test #4).
2. **`PlacedOrder --> PaymentMethod`:** a data record pointing at a *service* class. It should point to a `PaymentType` enum.
3. **`place_order(...) bool`:** the service creates a `PlacedOrder` but returns `bool`, which loses information.
4. **`Status`** should become `OrderStatus` with `PLACED` / `PAYMENT_FAILED`.

When you fix these on Saturday, update the diagram too. Keep the code and the diagram in sync.
