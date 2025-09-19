# --------------------------------------------------------
# FastAPI CRUD Application
# --------------------------------------------------------
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel 
import mysql.connector
from mysql.connector import pooling, Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Simple E-commerce CRUD API",
    description="A simple CRUD API for managing customers and products using FastAPI and MySQL."
)

# --------------------------------------------------------
# This allows the frontend to run from different origins to communicate with this backend.
origins = [
    "http://localhost",
    "http://localhost:8080", 
    "http://127.0.0.1:8080", 
    "http://127.0.0.1:5500", 
    "null" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Pydantic models for data validation
class Customer(BaseModel):
    first_name: str
    last_name: str
    email: str
    address: str | None = None
    phone: str | None = None

class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    address: str | None = None
    phone: str | None = None

class Product(BaseModel):
    name: str
    price: float
    description: str | None = None
    stock_quantity: int

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    description: str | None = None
    stock_quantity: int | None = None

# --------------------------------------------------------
# Database Connection Setup (MySQL)
# --------------------------------------------------------

# Credentials are not displayed for this case
DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME", "ecommerce_db")
}

db_pool = None

# creating a database
def initialize_database():
    """Creates the database if it doesn't exist."""
    try:
        # Connect without specifying a database first
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"Database '{DB_CONFIG['database']}' ensured to exist.")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error initializing database: {e}")
        raise

# Initializing a database and creating a pool
try:
    initialize_database()
    db_pool = pooling.MySQLConnectionPool(
        pool_name="mysql_pool",
        pool_size=5,
        **DB_CONFIG
    )
    print("Database connection pool created successfully.")
except Error as e:
    print(f"Error creating database connection pool: {e}")
    exit("Application failed to start: Could not connect to the database.")

# Dependency to get a DB connection from the pool
def get_db_connection():
    """
    FastAPI dependency that provides a database connection from the pool.
    Ensures the connection is returned to the pool after the request is processed.
    """
    conn = None
    try:
        conn = db_pool.get_connection()
        yield conn
    finally:
        if conn and conn.is_connected():
            conn.close()

def get_cursor(conn: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    """Dependency that provides a standard cursor."""
    with conn.cursor() as cursor:
        yield cursor

def get_dict_cursor(conn: mysql.connector.MySQLConnection = Depends(get_db_connection)):
    """Dependency that provides a dictionary cursor."""
    with conn.cursor(dictionary=True) as cursor:
        yield cursor

def create_db_tables():
    """Initializes tables in the MySQL database if they don't exist."""
    # automatic connection handling
    with db_pool.get_connection() as conn:
        cursor = conn.cursor()
        # Create Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INT PRIMARY KEY AUTO_INCREMENT,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                address TEXT,
                phone VARCHAR(20)
            )
        """)
        # Create Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL UNIQUE,
                price DECIMAL(10, 2) NOT NULL,
                description TEXT,
                stock_quantity INT NOT NULL DEFAULT 0
            )
        """)
        conn.commit()
        cursor.close()

create_db_tables()


# --------------------------------------------------------
# CRUD Operations for Customers
# --------------------------------------------------------

@app.get("/customers", tags=["Customers"])
def get_customers(cursor = Depends(get_dict_cursor)):
    """Retrieve a list of all customers."""
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    return {"customers": customers}

@app.post("/customers", tags=["Customers"])
def create_customer(customer: Customer, cursor = Depends(get_cursor)):
    """Create a new customer."""
    try:
        cursor.execute("INSERT INTO customers (first_name, last_name, email, address, phone) VALUES (%s, %s, %s, %s, %s)",
                       (customer.first_name, customer.last_name, customer.email, customer.address, customer.phone))
        conn = cursor._connection
        conn.commit()
        customer_id = cursor.lastrowid
        return {"message": "Customer created successfully", "customer_id": customer_id}
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")

@app.get("/customers/{customer_id}", tags=["Customers"])
def get_customer(customer_id: int, cursor = Depends(get_dict_cursor)):
    """Retrieve a single customer by their ID."""
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer": customer}

@app.put("/customers/{customer_id}", tags=["Customers"])
def update_customer(customer_id: int, customer: CustomerUpdate, cursor = Depends(get_cursor)):
    """Update an existing customer."""
    update_data = customer.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    fields = [f"{key} = %s" for key in update_data.keys()]
    values = list(update_data.values())
    values.append(customer_id)

    query = f"UPDATE customers SET {', '.join(fields)} WHERE customer_id = %s"
    try:
        cursor.execute(query, values)
        conn = cursor._connection
        conn.commit()
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer updated successfully"}

@app.delete("/customers/{customer_id}", tags=["Customers"])
def delete_customer(customer_id: int, cursor = Depends(get_cursor)):
    """Delete a customer."""
    cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
    conn = cursor._connection
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

# --------------------------------------------------------
# CRUD Operations for Products
# --------------------------------------------------------

@app.get("/products", tags=["Products"])
def get_products(cursor = Depends(get_dict_cursor)):
    """Retrieve a list of all products."""
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return {"products": products}

@app.post("/products", tags=["Products"])
def create_product(product: Product, cursor = Depends(get_cursor)):
    """Create a new product."""
    try:
        cursor.execute("INSERT INTO products (name, price, description, stock_quantity) VALUES (%s, %s, %s, %s)",
                       (product.name, product.price, product.description, product.stock_quantity))
        conn = cursor._connection
        conn.commit()
        product_id = cursor.lastrowid
        return {"message": "Product created successfully", "product_id": product_id}
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")

@app.get("/products/{product_id}", tags=["Products"])
def get_product(product_id: int, cursor = Depends(get_dict_cursor)):
    """Retrieve a single product by its ID."""
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": product}

@app.put("/products/{product_id}", tags=["Products"])
def update_product(product_id: int, product: ProductUpdate, cursor = Depends(get_cursor)):
    """Update an existing product."""
    #  Pydantic's model_dump to get only the fields that were provided
    update_data = product.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    #
    fields = [f"{key} = %s" for key in update_data.keys()]
    values = list(update_data.values())
    values.append(product_id)

    query = f"UPDATE products SET {', '.join(fields)} WHERE product_id = %s"
    try:
        cursor.execute(query, values)
        conn = cursor._connection
        conn.commit()
    except Error as e:
        raise HTTPException(status_code=400, detail=f"Database error: {e}")

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}

@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(product_id: int, cursor = Depends(get_cursor)):
    """Delete a product."""
    cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
    conn = cursor._connection
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}
