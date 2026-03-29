from fastapi import Depends
from repositories.repositories import (
    AddCartRepository,
    GetCartRepository,
    UpdateCartRepository
)
from services.service import (
    AddCartService,
    GetCartService,
    UpdateCartService,
    OrderProcessService
)
from helpers import (
    FraudCheckHandler,
    InventoryHandler,
    PaymentHandler,
    ConfirmationHandler
)

# Repository Providers

def get_add_cart_repository():
    return AddCartRepository()

def get_get_cart_repository():
    return GetCartRepository()

def get_update_cart_repository():
    return UpdateCartRepository()

# Service Providers

def get_add_cart_service(
    repo: AddCartRepository = Depends(get_add_cart_repository)
):
    return AddCartService(repo)

def get_get_cart_service(
    repo: GetCartRepository = Depends(get_get_cart_repository)
):
    return GetCartService(repo)

def get_update_cart_service(
    repo: UpdateCartRepository = Depends(get_update_cart_repository)
):
    return UpdateCartService(repo)

def get_order_process_service():
    fraud = FraudCheckHandler()
    inventory = InventoryHandler()
    payment = PaymentHandler()
    confirmation = ConfirmationHandler()

    return OrderProcessService(
        fraud, inventory, payment, confirmation
    )
