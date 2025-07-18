from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # CHANGE THIS in production

# --- Database Connection ---
# --- Database Connection ---
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="your-username",
        password="your-password",
        database="your-database-name"
    )

# --- Product Fetch Helper ---
def get_products_by_category(category):
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM products WHERE category = %s"
    cursor.execute(query, (category,))
    products = cursor.fetchall()
    cursor.close()
    db.close()
    return products

# --- Authentication Routes ---

# Register GET
@app.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')

# Register POST
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash("Passwords do not match!")
        return redirect('/register')

    hashed_password = generate_password_hash(password)

    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
            (username, email, hashed_password)
        )
        conn.commit()
        flash("Registration successful! Please log in.")
        return redirect('/login')
    except mysql.connector.IntegrityError:
        flash("Email already registered!")
        return redirect('/register')
    finally:
        cursor.close()
        conn.close()

# Login GET
@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

# Login POST
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        print(f"User found: {user['email']}")
        if check_password_hash(user['password'], password):
            print("Password matched!")
            session['user_id'] = user['id']
            session['email'] = user['email']
            return redirect('/')
        else:
            print("Password mismatch!")
    else:
        print("No user found with this email!")

    flash("Invalid email or password!")
    return redirect('/login')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')
# --- Pages ---

# Home Page
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    # Fetch random products for each category (you can adjust the limit)
    latest_mobiles = get_products_by_category('mobiles')[:3]
    latest_moisturizer = get_products_by_category('moisturizer')[:3]
    latest_sunscreen = get_products_by_category('sunscreen')[:3]
    latest_sunglasses = get_products_by_category('sunglasses')[:2]
    
    # Combine all latest products (optional, but it can be displayed as a mix)
    latest_products = latest_mobiles + latest_moisturizer + latest_sunscreen + latest_sunglasses

    return render_template('index.html', latest_products=latest_products)

# Products Page
@app.route('/products')
def products():
    if 'user_id' not in session:
        return redirect('/login')
    
    mobiles = get_products_by_category('mobiles')[:3]
    smartwatches = get_products_by_category('smartwatches')[:2]
    electronics = mobiles + smartwatches

    facewash = get_products_by_category('facewash')[:1]
    moisturizer = get_products_by_category('moisturizer')[:2]
    sunscreen = get_products_by_category('sunscreen')[:2]
    skincare = facewash + moisturizer + sunscreen

    accessories = get_products_by_category('sunglasses')[:5]

    footwear = get_products_by_category('shoes')[:5]

    return render_template('products.html', 
                            electronics=electronics, 
                            skincare=skincare, 
                            accessories=accessories, 
                            footwear=footwear)


@app.route('/about')
def about():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('about.html')


# Electronics Page
@app.route('/electronics')
def electronics():
    if 'user_id' not in session:
        return redirect('/login')
    mobiles = get_products_by_category('mobiles')
    smartwatches = get_products_by_category('smartwatches')
    return render_template('electronics.html', mobiles=mobiles, smartwatches=smartwatches)

# Skincare Page
@app.route('/skincare')
def skincare():
    if 'user_id' not in session:
        return redirect('/login')
    facewash = get_products_by_category('facewash')
    moisturizer = get_products_by_category('moisturizer')
    sunscreen = get_products_by_category('sunscreen')
    return render_template('skincare.html', facewash=facewash, moisturizer=moisturizer, sunscreen=sunscreen)

# Accessories Page
@app.route('/accessories')
def accessories():
    if 'user_id' not in session:
        return redirect('/login')
    sunglasses = get_products_by_category('sunglasses')
    return render_template('accessories.html', sunglasses=sunglasses)

# Footwear Page
@app.route('/footwear')
def footwear():
    if 'user_id' not in session:
        return redirect('/login')
    shoes = get_products_by_category('shoes')
    return render_template('footwear.html', shoes=shoes)


# Top Deals Page
@app.route('/top_deals')
def top_deals():
    if 'user_id' not in session:
        return redirect('/login')

    # Fetch all needed products and sort by best_price
    mobiles = sorted(get_products_by_category('mobiles'), key=lambda x: x['best_price'])[:2]
    smartwatches = sorted(get_products_by_category('smartwatches'), key=lambda x: x['best_price'])[:1]
    facewash = sorted(get_products_by_category('facewash'), key=lambda x: x['best_price'])[:2]
    moisturizer = sorted(get_products_by_category('moisturizer'), key=lambda x: x['best_price'])[:2]
    sunscreen = sorted(get_products_by_category('sunscreen'), key=lambda x: x['best_price'])[:2]
    sunglasses = sorted(get_products_by_category('sunglasses'), key=lambda x: x['best_price'])[:2]
    shoes = sorted(get_products_by_category('shoes'), key=lambda x: x['best_price'])[:1]

    # Combine all products into one list
    top_deals_products = mobiles + smartwatches + facewash + moisturizer + sunscreen + sunglasses + shoes

    return render_template('top_deals.html', top_deals_products=top_deals_products)

# Search Route
@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect('/login')
    
    query = request.args.get('query')
    if not query:
        flash("Please enter a search term.")
        return redirect('/')

    db = connect_to_db()
    cursor = db.cursor(dictionary=True)
    
    search_query = f"%{query}%"
    cursor.execute("SELECT * FROM products WHERE product_title or category LIKE %s", (search_query,))
    
    products = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('search_results.html', products=products, query=query)

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)
