from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# -------------------------
# Product Database
# -------------------------

products = {
    1: {"name": "Wireless Mouse", "price": 499, "in_stock": True},
    2: {"name": "Notebook", "price": 99, "in_stock": True},
    3: {"name": "USB Hub", "price": 299, "in_stock": False},
    4: {"name": "Pen Set", "price": 49, "in_stock": True}
}

# -------------------------
# In-Memory Storage
# -------------------------

cart = []
orders = []
order_counter = 1


# -------------------------
# Models
# -------------------------

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# -------------------------
# Helper Functions
# -------------------------

def calculate_subtotal(product, quantity):
    return product["price"] * quantity


def calculate_grand_total():
    return sum(item["subtotal"] for item in cart)


# -------------------------
# Add to Cart
# -------------------------

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]

    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

    # Check if product already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_subtotal(product, item["quantity"])

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    subtotal = calculate_subtotal(product, quantity)

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


# -------------------------
# View Cart
# -------------------------

@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": calculate_grand_total()
    }


# -------------------------
# Remove Item
# -------------------------

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    raise HTTPException(status_code=404, detail="Item not found in cart")


# -------------------------
# Checkout
# -------------------------

@app.post("/cart/checkout")
def checkout(request: CheckoutRequest):

    global order_counter

    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    created_orders = []

    for item in cart:

        order = {
            "order_id": order_counter,
            "customer_name": request.customer_name,
            "delivery_address": request.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }

        orders.append(order)
        created_orders.append(order)

        order_counter += 1

    cart.clear()

    return {
        "message": "Order placed successfully",
        "orders_placed": created_orders,
        "grand_total": sum(o["total_price"] for o in created_orders)
    }


# -------------------------
# View Orders
# -------------------------

@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }