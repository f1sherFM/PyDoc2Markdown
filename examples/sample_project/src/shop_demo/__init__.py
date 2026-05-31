"""Small shop demo package for PyDoc2Markdown examples."""

from shop_demo.inventory import Inventory, Product
from shop_demo.orders import Order, OrderStatus, calculate_total

__all__ = [
    "Inventory",
    "Order",
    "OrderStatus",
    "Product",
    "calculate_total",
]
