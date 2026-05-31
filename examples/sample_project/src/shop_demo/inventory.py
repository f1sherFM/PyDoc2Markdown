"""Inventory models and helpers for the sample shop."""

from dataclasses import dataclass


@dataclass
class Product:
    """A product available in the shop.

    Args:
        sku: Stable product identifier.
        name: Human-readable product name.
        price: Unit price in the shop currency.
        stock: Number of available units.
    """

    sku: str
    name: str
    price: float
    stock: int = 0

    @property
    def available(self) -> bool:
        """Whether the product can be purchased."""
        return self.stock > 0


class Inventory:
    """In-memory product inventory.

    Args:
        products: Initial products keyed by SKU.
    """

    def __init__(self, products: dict[str, Product] | None = None) -> None:
        self._products = products or {}

    def add(self, product: Product) -> None:
        """Add or replace a product.

        Args:
            product: Product to store.
        """
        self._products[product.sku] = product

    def get(self, sku: str) -> Product:
        """Return a product by SKU.

        Args:
            sku: Product identifier.

        Returns:
            Matching product.

        Raises:
            KeyError: If the SKU is unknown.
        """
        return self._products[sku]
