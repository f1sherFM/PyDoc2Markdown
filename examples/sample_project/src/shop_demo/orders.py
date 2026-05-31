"""Order models and pricing helpers."""

from dataclasses import dataclass
from enum import Enum

from shop_demo.inventory import Product


class OrderStatus(Enum):
    """Lifecycle status for an order."""

    DRAFT = "draft"
    PAID = "paid"
    SHIPPED = "shipped"


@dataclass
class Order:
    """A customer order.

    Args:
        order_id: Public order identifier.
        items: Products included in the order.
        status: Current order status.
    """

    order_id: str
    items: list[Product]
    status: OrderStatus = OrderStatus.DRAFT

    def mark_paid(self) -> None:
        """Mark the order as paid."""
        self.status = OrderStatus.PAID


def calculate_total(items: list[Product], discount: float = 0.0) -> float:
    """Calculate the discounted order total.

    Args:
        items: Products to include in the total.
        discount: Discount ratio between 0 and 1.

    Returns:
        Total price after discount.

    Raises:
        ValueError: If discount is outside the accepted range.
    """
    if not 0 <= discount <= 1:
        raise ValueError("discount must be between 0 and 1")
    subtotal = sum(item.price for item in items)
    return subtotal * (1 - discount)
