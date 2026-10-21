from abc import abstractmethod, ABC 
from dataclasses import dataclass,field
from enum import Enum, auto 
from typing import Protocol
from decimal import Decimal


# class CustomerCategory(Enum):
#     REGULAR = auto()
#     PREMIUM = auto()
#     EMPLOYEE = auto()
#     STUDENT = auto()


# A frozen dataclass to store orders whch are placed and solve the bug aof final total ( urr subtotal is dispalyed )
class Status(Enum):
    SUCCESS = auto()
    FAILURE = auto()


@dataclass(frozen=True)
class Item:
    name : str 
    price : Decimal 
    qty : int 
 
@dataclass
class Order:
    items : tuple[Item,...] 

    # frozen=True only stops you from reassigning a field (placed.order = x fails). It does nothing about the inside of a list. Right now this runs fine:

    email : str

    def __post_init__(self)->None:
        if not self.items : 
            raise ValueError("Items list cannot be empty")

    @property
    def subtotal(self)->Decimal:
        total = Decimal("0")
        for item in self.items:
            total+=(item.price)*(item.qty)
        return total

    
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, subtotal:Decimal)->Decimal:
        pass

class PremiumDiscount(DiscountStrategy):
    def apply(self,subtotal:Decimal)->Decimal:
        return (Decimal("0.9")*subtotal).quantize(Decimal("0.01"))

class EmployeeDiscount(DiscountStrategy):
    def apply(self,subtotal:Decimal)->Decimal:
        return (Decimal("0.7")*subtotal).quantize(Decimal("0.01"))

class NoDiscount(DiscountStrategy):
    def apply(self,subtotal:Decimal)->Decimal:
        return subtotal


class PaymentMethod(ABC):

    @abstractmethod
    def pay(self, amount :Decimal)->bool:
        pass

class CardPayment(PaymentMethod):

    def pay(self,amount:Decimal)->bool:
        print(f"Payment of {amount} proesssed by Card")
        return True

    def refund(self,amount:Decimal)->bool:
        print(f"Refund of Rs. {amount} made to the Card")
        return True

class PayPalPayment(PaymentMethod):

    def pay(self,amount:Decimal)->bool:
        print(f"Payment of {amount} proesssed by PayPal")
        return True

    def refund(self,amount:Decimal)->bool:
            print(f"Refund of Rs. {amount} made to the PayPal")
            return True

# LSP/ISP fix: pay and refund are separate promises. GiftCard only promises pay().
class GiftCardPayment(PaymentMethod):

    def pay(self,amount:Decimal)->bool:
        print(f"Payment of {amount} proesssed by GiftCard")
        return True
    

class Refundable(Protocol):

    def refund(self,amount:Decimal)->bool:
        ...

@dataclass(frozen=True)
class PlacedOrder:
    order : Order
    amount_paid : Decimal
    payment_method : PaymentMethod
    status : Status

class OrderRepository(ABC):

    @abstractmethod
    def save(self, order : PlacedOrder)->None:
        ...


class InMemoryOrderRepository(OrderRepository):

    def __init__(self):
        self.orders : list[PlacedOrder] = []

    def save(self,order:PlacedOrder)->None:
        self.orders.append(order)
        print(f"Order of Rs.{order.amount_paid} saved to DB")

class Notifier(Protocol):

    def send(self,to:str,msg:str)->None:
        ...

class ConsoleNotifier:

    def send(self, to:str , msg: str)->None:
        print(f"{"-"*60}\n   To {to}\n   Message : {msg}\n{"-"*60}")


class OrderService:

    def __init__(self,repository : OrderRepository , notifier : Notifier)->None:
        self.repository = repository
        self.notifier = notifier

    def place_order(self,order: Order , discount : DiscountStrategy , payment : PaymentMethod)->bool:
        total_amount = discount.apply(order.subtotal)
        payment_status = payment.pay(total_amount)
        if payment_status == False:
            #alert in payment failure
            placed_order = PlacedOrder(order=order,amount_paid=Decimal("0"),payment_method=payment,status=Status.FAILURE)
            
            self.notifier.send(to=placed_order.order.email , msg = f"Order of Rs.{total_amount} not confirmed due to payment issue. Please Try Again")
            return False
        
        placed_order = PlacedOrder(order=order,amount_paid=total_amount,payment_method=payment,status=Status.SUCCESS)
        self.repository.save(placed_order)
        self.notifier.send(to=placed_order.order.email , msg = f"Order of Rs.{placed_order.amount_paid} has been confirmed")            
        return True

