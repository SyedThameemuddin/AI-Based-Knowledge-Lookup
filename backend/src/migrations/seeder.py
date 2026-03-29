# migrations/seeder.py

from repositories.database import Database
from repositories.schema.schema import Item, Customer


class Seeder:

    def __init__(self):
        self.db = Database()

    def seed_data(self):

        session = self.db.SessionLocal()

        try:

            print("Seeder running")

            if not session.query(Customer).first():

                customers = [
                    Customer(name="Syed", mail="syed@test.com"),
                    Customer(name="Kash", mail="kash@test.com"),
                    Customer(name="Tharun", mail="tharun@test.com"),
                    Customer(name="Vaishnavi", mail="vaishnavi@test.com"),
                    Customer(name="Vicky", mail="vicky@test.com")
                ]

                session.add_all(customers)
                session.flush()

                print("\nCustomers inserted:")

                for c in customers:
                    print(f"{c.name} -> ID: {c.customer_id}")


            if not session.query(Item).first():

                items = [
                    Item(name="Latte", price=200, available_quantity=100),
                    Item(name="Cappuccino", price=220, available_quantity=100),
                    Item(name="Americano", price=180, available_quantity=100),
                    Item(name="Mocha", price=240, available_quantity=100),
                    Item(name="Cold Coffee", price=210, available_quantity=100),
                    Item(name="Espresso", price=150, available_quantity=100),
                    Item(name="Milo", price=220, available_quantity=100),
                    Item(name="Hot Chocolate", price=230, available_quantity=100),
                    Item(name="Boost", price=100, available_quantity=100)
                ]

                session.add_all(items)
                session.flush()

                print("\nItems inserted:")

                for item in items:
                    print(f"{item.name} -> ID: {item.item_id}")

            session.commit()

            print("\n✓ Database seeded successfully")

        except Exception as e:

            session.rollback()

            print(f"✗ Error seeding database: {str(e)}")

            raise e

        finally:
            session.close()

    def run_startup_seeding(self):
        """Run seeding on FastAPI startup"""
        self.seed_data()


if __name__ == "__main__":

    seeder = Seeder()

    seeder.seed_data()