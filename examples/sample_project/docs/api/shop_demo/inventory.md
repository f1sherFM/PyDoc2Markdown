# inventory

Inventory models and helpers for the sample shop.

## Table of Contents

- [Classes](#classes)
  - [`Product`](#product)
    - [@property `available`](#product-available)
  - [`Inventory`](#inventory)
    - [`add`](#inventory-add)
    - [`get`](#inventory-get)

**Public API:**
- `Product`
- `Inventory`

## Classes

### `Product` (dataclass)
A product available in the shop.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `sku` | `str` | Stable product identifier. |
| `name` | `str` | Human-readable product name. |
| `price` | `float` | Unit price in the shop currency. |
| `stock` | `int` | Number of available units. |

#### Methods
<a id="product-available"></a>

##### @property `available`
Whether the product can be purchased.

**Returns:** `bool`
---
### `Inventory`
In-memory product inventory.

#### Constructor Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `products` | `dict[str, [Product](#product)] \| None` | `None` | Initial products keyed by SKU. |

#### Methods
<a id="inventory-add"></a>

##### `add`
Add or replace a product.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `product` | `[Product](#product)` | *required* | Product to store. |

<a id="inventory-get"></a>

##### `get`
Return a product by SKU.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `sku` | `str` | *required* | Product identifier. |

**Returns:** `[Product](#product)`
Matching product.

**Raises:**
- `KeyError`: If the SKU is unknown.

---
