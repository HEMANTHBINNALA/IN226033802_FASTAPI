from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="FastAPI — Day 4 Assignment (CRUD)")

# ==========================================
# ROOT ENDPOINT
# ==========================================
@app.get("/")
def home():
    return {
        "message": "Welcome to my FastAPI Assignment 3!", 
        "instruction": "Add /docs to the URL to see the Swagger UI testing page."
    }

# ==========================================
# INITIAL DATA (Restored to the original 4 products)
# ==========================================
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# Helper function to find a product by ID
def find_product(product_id: int):
    return next((p for p in products if p['id'] == product_id), None)

# Pydantic model for creating a new product
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True

# ==========================================
# FIXED ROUTES (Must go ABOVE dynamic ID routes)
# ==========================================

@app.get('/products')
def get_all_products():
    return {"products": products, "total": len(products)}

# --- Q5: Build GET /products/audit ---
@app.get('/products/audit')
def product_audit():
    in_stock_list  = [p for p in products if p['in_stock']]
    out_stock_list = [p for p in products if not p['in_stock']]
    stock_value    = sum(p['price'] * 10 for p in in_stock_list)
    priciest       = max(products, key=lambda p: p['price'])
    return {
        'total_products':    len(products),
        'in_stock_count':    len(in_stock_list),
        'out_of_stock_names': [p['name'] for p in out_stock_list],
        'total_stock_value':  stock_value,
        'most_expensive':    {'name': priciest['name'], 'price': priciest['price']},
    }

# --- BONUS: Apply a Category-Wide Discount ---
@app.put('/products/discount')
def bulk_discount(
    category: str = Query(..., description='Category to discount'),
    discount_percent: int = Query(..., ge=1, le=99, description='% off'),
):
    updated = []
    for p in products:
        if p['category'] == category:
            p['price'] = int(p['price'] * (1 - discount_percent / 100))
            updated.append(p)
    if not updated:
        return {'message': f'No products found in category: {category}'}
    return {
        'message':          f'{discount_percent}% discount applied to {category}',
        'updated_count':    len(updated),
        'updated_products': updated,
    }

# --- Q1: Add 2 New Products Using POST ---
@app.post('/products', status_code=status.HTTP_201_CREATED)
def add_product(product: NewProduct, response: Response):
    # Check for duplicates
    if any(p['name'].lower() == product.name.lower() for p in products):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Product already exists"}
    
    # Auto-generate ID
    next_id = max(p['id'] for p in products) + 1 if products else 1
    new_prod = {
        "id": next_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }
    products.append(new_prod)
    return {"message": "Product added", "product": new_prod}


# ==========================================
# DYNAMIC ID ROUTES
# ==========================================

@app.get('/products/{product_id}')
def get_single_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    return product

# --- Q2: Restock the USB Hub Using PUT ---
@app.put('/products/{product_id}')
def update_product(product_id: int, response: Response, price: Optional[int] = None, in_stock: Optional[bool] = None):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}
    
    # Update fields only if they were provided in the request
    if price is not None:
        product['price'] = price
    if in_stock is not None:
        product['in_stock'] = in_stock
        
    return {"message": "Product updated", "product": product}

# --- Q3: Delete a Product and Handle Missing IDs ---
@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
    
    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}