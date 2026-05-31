# inventory


Inventory models and helpers for the sample shop.



## Table of Contents


- [Classes](#classes)

  - [`Product`](#product)


    - [
@property
`available`](#available)



  - [`Inventory`](#inventory)


    - [

`add`](#add)

    - [

`get`](#get)










## Classes


### `Product` (dataclass)




A product available in the shop.

Args:
    sku: Stable product identifier.
    name: Human-readable product name.
    price: Unit price in the shop currency.
    stock: Number of available units.







#### Methods


##### @property `available`


Whether the product can be purchased.





**Returns:** `bool`









---

### `Inventory`




In-memory product inventory.

Args:
    products: Initial products keyed by SKU.







#### Methods


##### `add`


Add or replace a product.

Args:
    product: Product to store.



**Parameters:**

| Name | Type | Description |
|------|------|-------------|

| `product` | `[Product](#product)` | Product to store. |




**Returns:** `None`







##### `get`


Return a product by SKU.

Args:
    sku: Product identifier.

Returns:
    Matching product.

Raises:
    KeyError: If the SKU is unknown.



**Parameters:**

| Name | Type | Description |
|------|------|-------------|

| `sku` | `str` | Product identifier. |




**Returns:** `[Product](#product)`

Matching product.



**Raises:**

- `KeyError`: If the SKU is unknown.






---
