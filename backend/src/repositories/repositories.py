from sqlalchemy import func

from utils.exceptions.error_codes import ErrorCodeStatus
from constants.http_status import HttpStatusCode
from utils.exceptions.custom_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from repositories.schema.schema import Customer, Item, Order, OrderItem, ErrorLog
from utils.helpers import CoffeeShopHelper

class CoffeeShopRepositories:

    def __init__(self, db):
        self.db = db

    def place_order_repo(self, customer_id, items):
        
        try:

            with self.db.get_db() as session:

                print("\nRepo place_order_repo executing")

                customer = session.query(Customer).filter(
                    Customer.customer_id == customer_id
                ).first()

                if not customer:
                    return {"status": "invalid_customer"}

                order = Order(
                    customer_id=customer_id,
                    status="preparing",
                    total_price=0
                )

                session.add(order)
                session.flush()
                total_price = 0

                for item_data in items:

                    item_name = item_data["item_name"]
                    quantity = item_data["quantity"]

                    print(f"\nProcessing item: {item_name} qty {quantity}")

                    item = session.query(Item).filter(
                        Item.name.ilike(f"%{item_name}%"),
                        Item.is_available == True
                    ).first()

                    if not item:
                        return {"data": "item is not available"}

                    if item.available_quantity < quantity:
                        return {"data": "the quantity you asked is not available"}

                    price = item.price * quantity

                    total_price += price

                    order_item = OrderItem(
                        order_id=order.order_id,
                        item_id=item.item_id,
                        quantity=quantity,
                        price=item.price
                    )
                    
                    session.add(order_item)

                    item.available_quantity -= quantity

                order.total_price = total_price

                session.commit()
                print(f"\n item_available after detecting: {item.available_quantity}, order_id: {order.order_id}, total_price: {total_price}")
                print("\n Repo task done")
                return {
                    "status": "success",
                    "order_id": order.order_id,
                    "total_price": total_price
                }
                
        except Exception as e:

            helper = CoffeeShopHelper()

            helper.error_logger(
                function_name="place_order_repo",
                file_name=__file__,
                error=str(e)
            )

            raise CustomAppException(
                message=f"Repository error: {str(e)}",
                code=ErrorCode.DATABASE_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus.get(ErrorCode.DATABASE_ERROR, "OM_SQL_005")
            )
            
    def check_order_status_repo(self, order_id):

        try:
            with self.db.get_db() as session:

                order = session.query(Order).filter(
                    Order.order_id == order_id
                ).first()

                if not order:
                    print("\nOrder not found")
                    return {"status": "order_not_found"}

                print(f"\n order_status: {order.status}, total_price: {order.total_price}")
                print("\n Repo task done")
                return {
                    "status": order.status,
                    "total_price": order.total_price
                }
                
        except Exception as e:

            helper = CoffeeShopHelper()

            helper.error_logger(
                function_name="place_order_repo",
                file_name=__file__,
                error=str(e)
            )

            raise CustomAppException(
                message=f"Repository error: {str(e)}",
                code=ErrorCode.DATABASE_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus.get(ErrorCode.DATABASE_ERROR, "OM_SQL_005")
            )
            
    def get_top_drinks_repo(self, limit):
        
        try:
            
            with self.db.get_db() as session:

                result = (
                    session.query(
                        Item.name,
                        func.count(OrderItem.item_id)
                    )
                    .join(Item.order_items)
                    .group_by(Item.name)
                    .order_by(func.count(OrderItem.item_id).desc())
                    .limit(limit)
                    .all()
                )
                
                print(f"\nResult of top drinks query: {result}")
                drinks = [r[0] for r in result]
                
                print(f"\nDrinks: {drinks}")
                print("\n Repo task done")
                return {"top_drinks": drinks}
        
        except Exception as e:

            helper = CoffeeShopHelper()

            helper.error_logger(
                function_name="place_order_repo",
                file_name=__file__,
                error=str(e)
            )

            raise CustomAppException(
                message=f"Repository error: {str(e)}",
                code=ErrorCode.DATABASE_ERROR,
                status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                error_code_id=ErrorCodeStatus.get(ErrorCode.DATABASE_ERROR, "OM_SQL_005")
            )
            
    def insert_error_log_repo(self, function_name, file_name, error):

        try:

            with self.db.get_db() as session:

                print("\nRepo insert_error_log_repo executing")

                error_log = ErrorLog(
                    function_name=function_name,
                    file_name=file_name,
                    error=error
                )

                session.add(error_log)
                session.commit()

                print("\nError log inserted successfully")

        except Exception as e:

            print("\nError while inserting error log:", str(e))