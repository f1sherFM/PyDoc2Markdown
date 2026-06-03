# inventory

Inventory models and helpers for the sample shop.

## Table of Contents

- [Classes](#classes)
  - [`Product`](#product)
    - [@property `available`](#product-available)
  - [`Inventory`](#inventory)
    - [`add`](#inventory-add)
    - [`get`](#inventory-get)

## Classes

### `Product` (dataclass)
A product available in the shop.

Args:
    sku: Stable product identifier.
    name: Human-readable product name.
    price: Unit price in the shop currency.
    stock: Number of available units.

#### Methods

<a id="product-available"></a>

##### @property `available`
Whether the product can be purchased.

**Returns:** `bool`
---

### `Inventory`
In-memory product inventory.

Args:
    products: Initial products keyed by SKU.

#### Methods

<a id="inventory-add"></a>

##### `add`
Add or replace a product.

Args:
    product: Product to store.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `product` | `[Product](#product)` | *required* | Product to store. |

<a id="inventory-get"></a>

##### `get`
Return a product by SKU.

Args:
    sku: Product identifier.

Returns:
    Matching product.

Raises:
    KeyError: If the SKU is unknown.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `sku` | `str` | *required* | Product identifier. |

**Returns:** `[Product](#product)`
Matching product.

**Raises:**
- `KeyError`: If the SKU is unknown.

---
