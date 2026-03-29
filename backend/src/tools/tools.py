from langchain_core.tools import tool
from langgraph.types import interrupt


class CoffeeShopTools:

    def __init__(self, service, customer_id):
        self.service = service
        self.customer_id = customer_id

    def get_tools(self):

        service = self.service
        customer_id = self.customer_id

        @tool
        def place_order(items: list):
            """Place a drinks order
            If user place an order for multiple drinks.
            items must be a list like:
            [
            {"item_name":"latte","quantity":2},
            {"item_name":"milo","quantity":1}
            ]
            """
            
            print("\nPlace order helper tool executing")
            print(f"\nItems received: {items}")
            
            decision = interrupt({
                "action": "place_order",
                "customer_id": customer_id,
                "items": items,
                "message": "Approve or reject this order"
            })
            
            print(f"\nDecision received after resume: {decision}")
            
            if decision != "approve":
                return {
                    "status": "rejected",
                    "message": "Order was rejected by the user. Do not proceed with order placement."
                }
                
            return service.place_order(customer_id, items)

        @tool
        def check_order_status(order_id: int):
            """Check Order status"""
            print("\nCheck order status helper tool executing")
            print(f"\nOrder ID: {order_id}")
            return service.check_order_status(order_id)

        @tool
        def get_top_drinks(limit):
            """Get top or famous drinks"""
            print("\nGet top drinks helper tool executing")
            print(f"\nLimit: {limit}")
            return service.get_top_drinks(limit)
        
        return [place_order, check_order_status, get_top_drinks]