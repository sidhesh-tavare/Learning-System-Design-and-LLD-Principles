from solid_demo import *


def main()->None:
    curr_db = InMemoryOrderRepository()
    curr_notifier = ConsoleNotifier()

    OrderA = Order(items = ( Item("A",Decimal("30.5"),4) ,(Item("B",Decimal("50"),2))),email="demo@gmail.com")
    OrderB = Order(items = (Item("A",Decimal("30.5"),4),),email="demo@gmail.com")

    order_service = OrderService(curr_db,curr_notifier)
    order_service.place_order(OrderA , PremiumDiscount() , CardPayment())
    order_service.place_order(OrderB , EmployeeDiscount() , GiftCardPayment())
    print(curr_db.orders)


if __name__ == "__main__":
    main()