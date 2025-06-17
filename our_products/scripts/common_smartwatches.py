import os
import pandas as pd
from rapidfuzz import process, fuzz

import os

# base folder
BASE_PATH = r"C:\Users\pranj\OneDrive\Desktop\mini_project\our_products\products"

# file names
files = {
    "amazon":   "amazon_smartwatches.csv",
    "flipkart": "flipkart_smartwatches.csv",
    "myntra":   "myntra_smartwatches.csv",
}

# build full paths
amazon   = pd.read_csv(os.path.join(BASE_PATH, files["amazon"]))
flipkart = pd.read_csv(os.path.join(BASE_PATH, files["flipkart"]))
myntra   = pd.read_csv(os.path.join(BASE_PATH, files["myntra"]))

# Create an empty list to store common products
common_products = []

# Set matching threshold
threshold = 57

# Compare Amazon products with Flipkart
for idx, row in amazon.iterrows():
    amazon_title = row['Title']
    
    # Find best match in Flipkart
    flipkart_match = process.extractOne(amazon_title, flipkart['Title'], scorer=fuzz.token_sort_ratio)

    if flipkart_match and flipkart_match[1] >= threshold:
        # Get matching row from Flipkart
        flipkart_row = flipkart[flipkart['Title'] == flipkart_match[0]].iloc[0]
        
        # Append matched product info
        common_products.append({
            'Amazon Title': amazon_title,
            'Amazon Price': row['Price'],
            'Amazon URL': row['Product URL'],
            'Amazon Image': row['Image URL'],
            
            'Flipkart Title': flipkart_row['Title'],
            'Flipkart Price': flipkart_row['Price'],
            'Flipkart URL': flipkart_row['Product URL'],
            'Flipkart Image': flipkart_row['Image URL'],
        })

BASE_PATH = r"C:\Users\pranj\OneDrive\Desktop\mini_project\our_products\common_products"

# After building the list common_products
common_df = pd.DataFrame(common_products)

# Save to the same folder
output_path = os.path.join(BASE_PATH, "common_smartwatches.csv")
common_df.to_csv(output_path, index=False)
print(f"✅ Saved {len(common_df)} records to {output_path}")