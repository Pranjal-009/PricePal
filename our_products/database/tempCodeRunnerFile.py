import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import os

# Define the path for the CSV files located in the 'common_products' directory
BASE_PATH = os.path.join(os.getcwd(), 'mini_project', 'our_products', 'common_products')

# Create the database if it doesn't exist
def create_database(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS pricepal")
        print("✅ Database created or already exists.")
    except mysql.connector.Error as err:
        print(f"❌ Failed creating database: {err}")
        exit(1)

# Create the products table
def create_table(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_title VARCHAR(255),
        amazon_price DECIMAL(10, 2),
        flipkart_price DECIMAL(10, 2),
        myntra_price DECIMAL(10, 2),
        best_price DECIMAL(10, 2),
        product_url TEXT,
        image_url TEXT,
        website VARCHAR(50)
    )
    """
    cursor.execute(create_table_query)
    print("✅ Table created or already exists.")

# Connect to MySQL
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pranjal@09",  # Replace with your actual password
        database="pricepal"
    )

# Safe price parser
def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

# Insert a product row
def insert_product(cursor, product):
    insert_query = """
        INSERT INTO products (
            product_title, amazon_price, flipkart_price, myntra_price,
            best_price, product_url, image_url, website
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (
        product['product_title'],
        product['amazon_price'],
        product['flipkart_price'],
        product['myntra_price'],
        product['best_price'],
        product['product_url'],
        product['image_url'],
        product['website']
    ))

# Process a CSV file
def process_csv(file_name, category, cursor, db):
    file_path = os.path.join(BASE_PATH, file_name)
    df = pd.read_csv(file_path)

    # ✅ Get available columns in the dataframe
    available_columns = df.columns.tolist()

    # 🚿 Drop rows where all titles are missing
    title_columns = ['Amazon Title', 'Flipkart Title', 'Myntra Title']
    title_columns = [col for col in title_columns if col in available_columns]
    
    if title_columns:
        df.dropna(subset=title_columns, how='all', inplace=True)

    # 🚿 Clean text columns (strip spaces and replace extra spaces)
    clean_columns = [
        'Amazon Title', 'Flipkart Title', 'Myntra Title',
        'Amazon URL', 'Flipkart URL', 'Myntra URL',
        'Amazon Image', 'Flipkart Image', 'Myntra Image'
    ]
    for col in clean_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)

    # 🚿 Clean price columns by removing non-numeric characters
    price_columns = ['Amazon Price', 'Flipkart Price', 'Myntra Price']
    for col in price_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    # Insert each row into the database
    for _, row in df.iterrows():
        amazon_price = safe_float(row.get('Amazon Price'))
        flipkart_price = safe_float(row.get('Flipkart Price'))
        myntra_price = safe_float(row.get('Myntra Price'))

        valid_prices = [(amazon_price, "Amazon"), (flipkart_price, "Flipkart"), (myntra_price, "Myntra")]
        valid_prices = [(p, s) for p, s in valid_prices if p is not None]

        if valid_prices:
            best_price, source = min(valid_prices)
        else:
            best_price, source = None, "Unknown"

        if source == "Amazon":
            product_url = row.get('Amazon URL')
            image_url = row.get('Amazon Image')
            product_title = row.get('Amazon Title')
        elif source == "Flipkart":
            product_url = row.get('Flipkart URL')
            image_url = row.get('Flipkart Image')
            product_title = row.get('Flipkart Title')
        elif source == "Myntra":
            product_url = row.get('Myntra URL')
            image_url = row.get('Myntra Image')
            product_title = row.get('Myntra Title')
        else:
            product_url = image_url = product_title = None

        product_data = {
            'product_title': product_title,
            'amazon_price': amazon_price,
            'flipkart_price': flipkart_price,
            'myntra_price': myntra_price,
            'best_price': best_price,
            'product_url': product_url,
            'image_url': image_url,
            'website': source
        }

        insert_product(cursor, product_data)

    db.commit()
    print(f"✅ Inserted cleaned data from {file_name}")


# Main function
def main():
    # Initial connection to create DB
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pranjal@09"  # Replace with your actual password
    )
    cursor = db.cursor()
    create_database(cursor)
    cursor.close()
    db.close()

    # Connect again, this time to the new DB
    db = connect_to_db()
    cursor = db.cursor()
    create_table(cursor)

    # Process all CSV files
    csv_files = [
        ("common_mobiles.csv", "mobiles"),
        ("common_smartwatches.csv", "smartwatches"),
        ("common_facewash.csv", "facewash"),
        ("common_moisturizer.csv", "moisturizer"),
        ("common_sunscreen.csv", "sunscreen"),
        ("common_shoes.csv", "shoes")
    ]

    for file_name, category in csv_files:
        print(f"📦 Processing {file_name}...")
        process_csv(file_name, category, cursor, db)

    cursor.close()
    db.close()
    print("🎉 All data inserted successfully!")

if __name__ == "__main__":
    main()
