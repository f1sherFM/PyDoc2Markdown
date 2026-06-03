# orders

Order models and pricing helpers.

## Table of Contents

- [Classes](#classes)
  - [`OrderStatus`](#orderstatus)
  - [`Order`](#order)
    - [`mark_paid`](#order-mark_paid)

- [Functions](#functions)
  - [`calculate_total`](#calculate_total)

## Classes

### `OrderStatus` (enum)
**Bases:** `Enum`

Lifecycle status for an order.

---

### `Order` (dataclass)
A customer order.

Args:
    order_id: Public order identifier.
    items: Products included in the order.
    status: Current order status.

#### Methods

<a id="order-mark_paid"></a>

##### `mark_paid`
Mark the order as paid.

---

## Functions

### `calculate_total`
Calculate the discounted order total.

Args:
    items: Products to include in the total.
    discount: Discount ratio between 0 and 1.

Returns:
    Total price after discount.

Raises:
    ValueError: If discount is outside the accepted range.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `items` | `list[[Product](#product)]` | *required* | Products to include in the total. |
| `discount` | `float` | `0.0` | Discount ratio between 0 and 1. |

**Returns:** `float`
Total price after discount.

**Raises:**
- `ValueError`: If discount is outside the accepted range.
