from decimal import Decimal
import hashlib
import os
import sqlite3
import uuid
import json
from flask import Flask, request, jsonify, render_template
import pymysql
from flask_cors import CORS
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules

app = Flask(__name__)
CORS(app)

# Database Connection Function
def connect_db():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="okay",
            database="ecom_web"
        )
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

# Serve HTML Page
@app.route('/')
def home():
    return render_template('index.html')

# Function to hash a password
def hash_password(password):
    salt = os.urandom(32)  # Generate a random salt
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + hashed_password  # Store salt with the hash

# Function to verify a password
def verify_password(stored_password, provided_password):
    salt = stored_password[:32]  # Extract the salt from the stored password
    stored_hash = stored_password[32:]  # Extract the hash
    hashed_provided_password = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return hashed_provided_password == stored_hash  # Compare the hashes

# User Registration API
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    required_fields = ["name", "email", "phone", "address", "age", "gender", "category", "budget", "payment", "password"]

    # Check if required fields are missing
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Required fields are missing!"}), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed!"}), 500
        
        cursor = conn.cursor()

        # Check if the user already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (data["email"],))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"error": "User  already exists!"}), 400

        # Hash the password
        hashed_password = hash_password(data["password"])

        # Insert a new user record
        query = """
            INSERT INTO users (name, email, phone, address, age, gender, category, budget, payment_method, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data["name"], data["email"], data["phone"], data["address"],
            data["age"], data["gender"], data["category"],
            data["budget"], data["payment"],
            hashed_password  # Store the hashed password
        ))
        conn.commit()
        return jsonify({"message": "User  registered successfully!"}), 201

    except Exception as e:
        print(f"Error registering user: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()  # Always close the connection

# User Login API
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    required_fields = ["email", "password"]

    # Check if required fields are missing
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Required fields are missing!"}), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed!"}), 500
        
        cursor = conn.cursor()

        # Fetch user details
        cursor.execute("SELECT password FROM users WHERE email = %s", (data["email"],))
        user = cursor.fetchone()

        if user is None:
            return jsonify({"error": "User  not found!"}), 404

        # Verify password
        if verify_password(user[0], data["password"]):
            return jsonify({"message": "Login successful!"}), 200
        else:
            return jsonify({"error": "Invalid password!"}), 401

    except Exception as e:
        print(f"Error logging in user: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

@app.route('/search', methods=['GET'])
def search_products():
    search_query = request.args.get('query', '').lower()
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Query to fetch products based on the search term
        cursor.execute("SELECT id, name, category, price, image_url FROM products WHERE LOWER(category) LIKE %s", ('%' + search_query + '%',))
        products = cursor.fetchall()

        results = []
        for prod in products:
            results.append({
                "id": prod[0],
                "name": prod[1],
                "category": prod[2],
                "price": float(prod[3]),
                "image_url": prod[4]
            })

        return jsonify({"products": results}), 200

    except Exception as e:
        print(f"Search Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        

@app.route('/save_products', methods=['POST'])
def save_products():
    try:
        data = request.json  # Get the JSON data from the request
        conn = connect_db()
        cursor = conn.cursor()

        for product in data:
            product_id = product.get("id")  # Get product ID

            # Check if the product already exists
            cursor.execute("SELECT COUNT(*) FROM products WHERE id = %s", (product_id,))
            exists = cursor.fetchone()[0]

            if exists:
                print(f"Product with ID {product_id} already exists. Skipping insertion.")
                continue  # Skip this product or handle it as needed

            # Insert product into the database
            query = """
                INSERT INTO products (id, name, category, price, image_url)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                product_id, product["name"], product["category"],
                product["price"], product["image_url"]
            ))

        conn.commit()  # Commit the transaction
        return jsonify({"message": "Products saved successfully!"}), 201

    except Exception as e:
        print(f"Error saving products: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()  # Always close the connection

# Save Transaction API
@app.route('/save_transaction', methods=['POST'])
def save_transaction():
    try:
        data = request.json
        user_email = data.get("user_email")  # Ensure correct field names
        cart_items = data.get("items", [])

        if not user_email or not cart_items:
            return jsonify({"error": "Missing user email or cart items"}), 400

        conn = connect_db()
        cursor = conn.cursor()

        # Generate a unique transaction ID for this checkout session
        transaction_id = str(uuid.uuid4())[:8]  

        # Prepare the transaction data
        transaction_data = []
        total_price = 0

        for item in cart_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if not product_id or not quantity:
                continue

            # Fetch product details
            cursor.execute("SELECT name, price FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()

            if not product:
                continue

            product_name, product_price = product

            if isinstance(product_price, Decimal):
                product_price = float(product_price)

            item_total_price = product_price * quantity
            total_price += item_total_price

            # Append item details to transaction data
            transaction_data.append({
                "product_id": product_id,
                "product_name": product_name,
                "quantity": quantity,
                "total_price": item_total_price
            })

        # Store all items under the same `transaction_id` in a single row
        query = """
            INSERT INTO transactions (transaction_id, user_email, items, total_price)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (transaction_id, user_email, json.dumps(transaction_data), float(total_price)))

        conn.commit()
        conn.close()

        print("✅ Transaction saved successfully!")  
        return jsonify({"message": "Transaction saved successfully!", "transaction_id": transaction_id}), 201

    except Exception as e:
        print(f"❌ ERROR in save_transaction: {e}")  
        return jsonify({"error": str(e)}), 500

# Get Most Bought Products
@app.route('/most_bought', methods=['GET'])
def most_bought_products():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch the top 4 most bought products
        cursor.execute("""
            SELECT product_id, COUNT(*) as purchase_count
            FROM transactions
            JOIN JSON_TABLE(items, '$[*]' COLUMNS (product_id VARCHAR(255) PATH '$.product_id')) AS jt
            GROUP BY product_id
            ORDER BY purchase_count DESC
            LIMIT 4
        """)
        most_bought = cursor.fetchall()

        results = []
        for product_id, purchase_count in most_bought:
            cursor.execute("SELECT id, name, category, price, image_url FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            if product:
                results.append({
                    "id": product[0],
                    "name": product[1],
                    "category": product[2],
                    "price": float(product[3]),
                    "image_url": product[4],
                    "purchase_count": purchase_count
                })

        return jsonify({"most_bought_products": results}), 200

    except Exception as e:
        print(f"Error fetching most bought products: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()



@app.route('/recommendations/<user_email>', methods=['GET'])
def recommend_products(user_email):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch all transactions for the user
        cursor.execute("SELECT items FROM transactions WHERE user_email = %s", (user_email,))
        user_transactions = cursor.fetchall()

        # Aggregate all items from the user's transactions
        user_items = []
        for items_json in user_transactions:
            items = json.loads(items_json[0])  # Assuming items_json is a tuple
            user_items.extend([item["product_id"] for item in items])

        print("User 's all transaction items:", user_items)

        # Fetch all transactions to create the basket for Apriori
        cursor.execute("SELECT items FROM transactions")
        transactions = cursor.fetchall()

        # Convert to DataFrame for Apriori
        basket = []
        for items_json in transactions:
            items = json.loads(items_json[0])  # Assuming items_json is a tuple
            basket.append([item["product_id"] for item in items])

        # Create transaction dataframe
        from mlxtend.preprocessing import TransactionEncoder
        te = TransactionEncoder()
        te_ary = te.fit(basket).transform(basket)
        df = pd.DataFrame(te_ary, columns=te.columns_)

        # Apply Apriori
        frequent_itemsets = apriori(df, min_support=0.01, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)

        # Check if the user has any transactions
        if not user_items:
            print("No transactions found for user:", user_email)
            # If no transactions found, suggest based on most bought products
            cursor.execute("""
                SELECT product_id 
                FROM transactions 
                JOIN JSON_TABLE(items, '$[*]' COLUMNS (product_id VARCHAR(255) PATH '$.product_id')) AS jt 
                GROUP BY product_id 
                ORDER BY COUNT(*) DESC 
                LIMIT 4
            """)
            common_products = cursor.fetchall()
            recommended = [prod[0] for prod in common_products]
            print("Common products recommended:", recommended)
        else:
            # Filter recommendations based on all user items
            recommended = set()
            for _, row in rules.iterrows():
                if set(row['antecedents']).issubset(set(user_items)):
                    recommended.update(row['consequents'])
            print("Recommended products based on all transactions:", recommended)

        recommended = list(recommended)[:5] 

        if not recommended:
            return jsonify({"message": "No recommendations found"}), 200

        # Fetch product details for recommended products
        format_strings = ','.join(['%s'] * len(recommended))
        cursor.execute(f"SELECT id, name, category, price, image_url FROM products WHERE id IN ({format_strings})", tuple(recommended))
        recommended_products = cursor.fetchall()

        results = []
        for prod in recommended_products:
            results.append({
                "id": prod[0],
                "name": prod[1],
                "category": prod[2],
                "price": float(prod[3]),
                "image_url": prod[4]
            })

        return jsonify({"recommended_products": results}), 200

    except Exception as e:
        print(f"Recommendation Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)